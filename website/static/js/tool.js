/**
 * tool.js
 * -------
 * Interactive analysis tool for the surface_dipole_library website.
 *
 * State management, atom table rendering, preset loading,
 * API communication, and results rendering.
 */

'use strict';

// ─── State ──────────────────────────────────────────────────────────────────

/** @type {Array<{element: string, charge: number, x: number, y: number, z: number, label: string}>} */
let atomRows = [];

/** Sort state for the results table: { col: number, asc: boolean } */
let sortState = { col: 0, asc: true };

/** Cache of the last results returned from the API */
let lastResults = null;


// ─── Preset data ─────────────────────────────────────────────────────────────

const PRESETS = {
  tio2: [
    { element: 'Ti', charge:  0.580, x: 0.00, y: 0.00, z: 3.50, label: 'Ti5c1_film' },
    { element: 'Ti', charge:  0.580, x: 2.96, y: 0.00, z: 3.50, label: 'Ti5c2_film' },
    { element: 'Ti', charge:  0.580, x: 1.48, y: 3.25, z: 3.50, label: 'Ti5c3_film' },
    { element: 'Ti', charge:  0.480, x: 1.48, y: 1.48, z: 4.50, label: 'Ti6c1_film' },
    { element: 'O',  charge: -0.290, x: 1.48, y: 0.00, z: 4.20, label: 'O_br1_film' },
    { element: 'O',  charge: -0.290, x: 4.44, y: 0.00, z: 4.20, label: 'O_br2_film' },
    { element: 'O',  charge: -0.290, x: 2.96, y: 3.25, z: 4.20, label: 'O_br3_film' },
    { element: 'O',  charge: -0.260, x: 0.00, y: 1.62, z: 3.80, label: 'O_ip1_film' },
    { element: 'O',  charge: -0.260, x: 2.96, y: 1.62, z: 3.80, label: 'O_ip2_film' },
    { element: 'O',  charge: -0.200, x: 0.00, y: 0.00, z: 5.20, label: 'O_OH1_film' },
    { element: 'H',  charge:  0.180, x: 0.00, y: 0.96, z: 5.80, label: 'H_OH1_film' },
  ],

  ito: [
    { element: 'In', charge:  0.780, x: 0.00, y: 0.00, z: 3.50, label: 'In5c1_film' },
    { element: 'In', charge:  0.780, x: 3.58, y: 0.00, z: 3.50, label: 'In5c2_film' },
    { element: 'In', charge:  0.780, x: 1.79, y: 3.10, z: 3.50, label: 'In5c3_film' },
    { element: 'Sn', charge:  0.950, x: 1.79, y: 1.03, z: 3.50, label: 'Sn_dp1_film' },
    { element: 'O',  charge: -0.390, x: 1.79, y: 0.00, z: 4.30, label: 'O_br1_film' },
    { element: 'O',  charge: -0.390, x: 0.90, y: 1.55, z: 4.30, label: 'O_br2_film' },
    { element: 'O',  charge: -0.390, x: 2.69, y: 1.55, z: 4.30, label: 'O_br3_film' },
    { element: 'O',  charge: -0.390, x: 4.48, y: 1.55, z: 4.30, label: 'O_br4_film' },
    { element: 'O',  charge: -0.520, x: 0.00, y: 0.00, z: 4.90, label: 'O_term1_film' },
    { element: 'O',  charge: -0.520, x: 3.58, y: 0.00, z: 4.90, label: 'O_term2_film' },
    { element: 'O',  charge: -0.520, x: 1.79, y: 3.10, z: 4.90, label: 'O_term3_film' },
  ],
};


// ─── Atom management ─────────────────────────────────────────────────────────

/**
 * Add an atom to the state array and re-render the table.
 * @param {string}  element
 * @param {number}  charge
 * @param {number}  x
 * @param {number}  y
 * @param {number}  z
 * @param {string}  label
 */
function addAtom(element = 'O', charge = -0.29, x = 0, y = 0, z = 3.5, label = '') {
  atomRows.push({ element, charge, x, y, z, label });
  renderAtomTable();
}

/**
 * Remove atom at the given index and re-render.
 * @param {number} index
 */
function removeAtom(index) {
  atomRows.splice(index, 1);
  renderAtomTable();
}

/**
 * Load a named preset, replacing atomRows entirely.
 * @param {'tio2'|'ito'} name
 */
function loadExample(name) {
  const preset = PRESETS[name];
  if (!preset) return;

  // Deep copy to avoid mutating the preset
  atomRows = preset.map(a => ({ ...a }));
  renderAtomTable();
  hideResults();
  hideError();
}


// ─── Table rendering ─────────────────────────────────────────────────────────

/** Re-render the entire atom input table from the atomRows state. */
function renderAtomTable() {
  const table   = document.getElementById('atomTable');
  const empty   = document.getElementById('atomEmptyState');
  const tbody   = document.getElementById('atomTableBody');
  const counter = document.getElementById('atomCount');

  counter.textContent = atomRows.length;

  if (atomRows.length === 0) {
    table.classList.add('d-none');
    empty.classList.remove('d-none');
    return;
  }

  table.classList.remove('d-none');
  empty.classList.add('d-none');

  tbody.innerHTML = '';
  atomRows.forEach((atom, i) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${i + 1}</td>
      <td>
        <input type="text" value="${escHtml(atom.element)}"
               style="width:38px" maxlength="3"
               onchange="updateAtom(${i}, 'element', this.value)" />
      </td>
      <td>
        <input type="number" value="${atom.charge}" step="0.001"
               style="width:60px"
               onchange="updateAtom(${i}, 'charge', parseFloat(this.value))" />
      </td>
      <td>
        <input type="number" value="${atom.x}" step="0.01"
               style="width:52px"
               onchange="updateAtom(${i}, 'x', parseFloat(this.value))" />
      </td>
      <td>
        <input type="number" value="${atom.y}" step="0.01"
               style="width:52px"
               onchange="updateAtom(${i}, 'y', parseFloat(this.value))" />
      </td>
      <td>
        <input type="number" value="${atom.z}" step="0.01"
               style="width:52px"
               onchange="updateAtom(${i}, 'z', parseFloat(this.value))" />
      </td>
      <td>
        <input type="text" value="${escHtml(atom.label)}"
               style="width:90px" placeholder="auto"
               onchange="updateAtom(${i}, 'label', this.value)" />
      </td>
      <td>
        <button class="btn-remove" onclick="removeAtom(${i})" title="Remove atom">
          <i class="bi bi-x-lg"></i>
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

/**
 * Update a field in an existing atom row.
 * @param {number} index
 * @param {string} field
 * @param {*}      value
 */
function updateAtom(index, field, value) {
  if (index >= 0 && index < atomRows.length) {
    atomRows[index][field] = value;
  }
}


// ─── Analysis submission ──────────────────────────────────────────────────────

/** Validate inputs, build payload, POST to /api/analyze, show results. */
async function submitAnalysis() {
  hideError();

  if (atomRows.length === 0) {
    showError('Please add at least one film atom or load an example.');
    return;
  }

  const cutoffInput = document.getElementById('cutoff');
  const cutoff = parseFloat(cutoffInput.value);
  if (isNaN(cutoff) || cutoff <= 0) {
    showError('Cutoff must be a positive number in Angstroms.');
    return;
  }

  const glassVariant = document.getElementById('glassVariant').value;

  // Collect atom data from the current state (values may have been edited)
  const film_atoms = atomRows.map(a => ({
    element:  String(a.element).trim(),
    charge:   Number(a.charge),
    position: [Number(a.x), Number(a.y), Number(a.z)],
    label:    a.label ? String(a.label).trim() : undefined,
  }));

  setLoading(true);
  hideResults();

  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ film_atoms, cutoff, glass_variant: glassVariant }),
    });

    const data = await response.json();

    if (!response.ok || data.error) {
      showError(data.error || `Server error ${response.status}`);
      return;
    }

    lastResults = data;
    renderResults(data);

  } catch (err) {
    showError('Network error — could not reach the server. Is Flask running?');
    console.error('API error:', err);
  } finally {
    setLoading(false);
  }
}


// ─── Results rendering ────────────────────────────────────────────────────────

/**
 * Populate all results panels with the API response data.
 * @param {object} data  — full JSON response from /api/analyze
 */
function renderResults(data) {
  // ── Dipole cards ────────────────────────────────────────────────────────
  renderDipoleCard('glassDipoleContent', data.substrate_dipole, 'Glass');
  renderDipoleCard('filmDipoleContent',  data.film_dipole,      'Film');

  // ── Best interaction card ───────────────────────────────────────────────
  const best = data.best;
  document.getElementById('bestInteractionContent').innerHTML = `
    <div class="sdl-best-atoms">
      <span class="sdl-best-atom">${escHtml(best.substrate_atom)}</span>
      <span class="sdl-best-arrow">&#8644;</span>
      <span class="sdl-best-atom">${escHtml(best.film_atom)}</span>
    </div>
    <div class="sdl-best-details">
      <div class="sdl-best-detail">
        <div class="sdl-best-detail-label">Energy</div>
        <div class="sdl-best-detail-val">${best.energy_eV.toFixed(4)} eV</div>
      </div>
      <div class="sdl-best-detail">
        <div class="sdl-best-detail-label">Distance</div>
        <div class="sdl-best-detail-val">${best.distance_ang.toFixed(3)} Å</div>
      </div>
      <div class="sdl-best-detail">
        <div class="sdl-best-detail-label">Glass q</div>
        <div class="sdl-best-detail-val">${formatCharge(best.substrate_charge)}</div>
      </div>
      <div class="sdl-best-detail">
        <div class="sdl-best-detail-label">Film q</div>
        <div class="sdl-best-detail-val">${formatCharge(best.film_charge)}</div>
      </div>
      <div class="sdl-best-detail">
        <div class="sdl-best-detail-label">Type</div>
        <div class="sdl-best-detail-val">
          <span class="sdl-type-badge ${escHtml(best.interaction_type)}">${escHtml(best.interaction_type)}</span>
        </div>
      </div>
    </div>
  `;

  // ── Stats ───────────────────────────────────────────────────────────────
  document.getElementById('statTotal').textContent     = data.n_pairs;
  document.getElementById('statAttractive').textContent = data.stats.attractive;
  document.getElementById('statRepulsive').textContent  = data.stats.repulsive;

  const variant = data.glass_variant.replace(/_/g, ' ');
  document.getElementById('tableSubtitle').textContent =
    `${data.n_pairs} pairs — ${variant} glass — ${data.n_atoms_film} film atoms`;

  // ── Interaction table ───────────────────────────────────────────────────
  renderInteractionTable(data.pairs);

  // Show results panel
  document.getElementById('resultsPlaceholder').classList.add('d-none');
  document.getElementById('resultsContent').classList.remove('d-none');
}

/**
 * Render a single dipole card.
 * @param {string} containerId
 * @param {object} d  — dipole dict from API
 * @param {string} name
 */
function renderDipoleCard(containerId, d, name) {
  document.getElementById(containerId).innerHTML = `
    <div class="sdl-dipole-value">${d.magnitude.toFixed(4)} e·Å</div>
    <div class="sdl-dipole-unit">${d.debye.toFixed(3)} Debye</div>
    <div class="sdl-dipole-components">
      μx = ${formatNum(d.mu_x, 4)}<br>
      μy = ${formatNum(d.mu_y, 4)}<br>
      μz = ${formatNum(d.mu_z, 4)}<br>
      Q  = ${formatCharge(d.total_charge)}
    </div>
  `;
}

/**
 * Render the full ranked interaction table.
 * @param {Array} pairs
 */
function renderInteractionTable(pairs) {
  const tbody = document.getElementById('resultsTableBody');
  tbody.innerHTML = '';

  pairs.forEach(p => {
    const tr = document.createElement('tr');
    tr.setAttribute('data-type', p.interaction_type);

    const energyClass = p.energy_eV < 0
      ? 'text-success fw-semibold'
      : (p.energy_eV > 0 ? 'text-danger fw-semibold' : '');

    tr.innerHTML = `
      <td><span class="sdl-rank-badge">${p.rank}</span></td>
      <td><code>${escHtml(p.substrate_atom)}</code></td>
      <td><code>${escHtml(p.film_atom)}</code></td>
      <td>${formatCharge(p.substrate_charge)}</td>
      <td>${formatCharge(p.film_charge)}</td>
      <td>${p.distance_ang.toFixed(3)}</td>
      <td class="${energyClass}">${p.energy_eV.toFixed(4)}</td>
      <td><span class="sdl-type-badge ${escHtml(p.interaction_type)}">${escHtml(p.interaction_type)}</span></td>
    `;
    tbody.appendChild(tr);
  });

  // Reset sort indicators
  document.querySelectorAll('#resultsTable thead th').forEach(th => {
    th.classList.remove('sort-asc', 'sort-desc');
  });
  sortState = { col: 0, asc: true };
}


// ─── Table sorting ────────────────────────────────────────────────────────────

/**
 * Sort the results table by the given column index.
 * Clicking the same column toggles ascending/descending.
 * @param {number} colIndex
 */
function sortTable(colIndex) {
  if (sortState.col === colIndex) {
    sortState.asc = !sortState.asc;
  } else {
    sortState.col = colIndex;
    sortState.asc = true;
  }

  const tbody   = document.getElementById('resultsTableBody');
  const rows    = Array.from(tbody.querySelectorAll('tr'));
  const headers = document.querySelectorAll('#resultsTable thead th');

  // Update header icons
  headers.forEach((th, i) => {
    th.classList.remove('sort-asc', 'sort-desc');
    if (i === colIndex) {
      th.classList.add(sortState.asc ? 'sort-asc' : 'sort-desc');
    }
  });

  rows.sort((a, b) => {
    const cellA = a.cells[colIndex] ? a.cells[colIndex].textContent.trim() : '';
    const cellB = b.cells[colIndex] ? b.cells[colIndex].textContent.trim() : '';

    const numA = parseFloat(cellA);
    const numB = parseFloat(cellB);

    let cmp;
    if (!isNaN(numA) && !isNaN(numB)) {
      cmp = numA - numB;
    } else {
      cmp = cellA.localeCompare(cellB);
    }

    return sortState.asc ? cmp : -cmp;
  });

  rows.forEach(r => tbody.appendChild(r));
}


// ─── UI helpers ──────────────────────────────────────────────────────────────

function setLoading(on) {
  const btn     = document.getElementById('analyzeBtn');
  const normal  = document.getElementById('analyzeNormal');
  const spinner = document.getElementById('analyzeSpinner');

  btn.disabled = on;
  normal.classList.toggle('d-none', on);
  spinner.classList.toggle('d-none', !on);
}

function showError(msg) {
  const el = document.getElementById('errorAlert');
  document.getElementById('errorMsg').textContent = msg;
  el.classList.remove('d-none');
}

function hideError() {
  document.getElementById('errorAlert').classList.add('d-none');
}

function hideResults() {
  document.getElementById('resultsContent').classList.add('d-none');
  document.getElementById('resultsPlaceholder').classList.remove('d-none');
}


// ─── Formatting utilities ─────────────────────────────────────────────────────

function escHtml(str) {
  if (str == null) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/**
 * Format a number with sign and fixed decimal places.
 * @param {number} val
 * @param {number} places
 * @returns {string}
 */
function formatNum(val, places = 4) {
  const s = val.toFixed(places);
  return val >= 0 ? '+' + s : s;
}

/**
 * Format a charge value with sign.
 * @param {number} q
 * @returns {string}
 */
function formatCharge(q) {
  const s = q.toFixed(3);
  return q >= 0 ? '+' + s : s;
}


// ─── Init ─────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  renderAtomTable();

  // Allow Ctrl+Enter to submit
  document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      submitAnalysis();
    }
  });
});
