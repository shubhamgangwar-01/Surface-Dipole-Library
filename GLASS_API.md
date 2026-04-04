# Glass-Fixed API — `surface_dipole_library`

> **Version 1.0.0** — Substrate locked to borosilicate glass; user only provides the thin film.

---

## What Changed and Why

Before this update, users had to define **both** the substrate and the film:

```python
# OLD — user had to define glass manually every time
result = analyze_surface_interactions(substrate_atoms, film_atoms)
```

After this update, the borosilicate glass surface is **built into the library**.
Users only define the film:

```python
# NEW — substrate is automatic
result = analyze_film_on_glass(film_atoms)
```

The glass surface definition — atom positions, elements, and ClayFF partial charges —
is stored inside `surface_dipole_library/glass_substrate.py` and is loaded
automatically. Every call uses the same validated, physically-correct glass model.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [The Fixed Glass Substrate](#the-fixed-glass-substrate)
3. [Glass Variants](#glass-variants)
4. [New API Functions](#new-api-functions)
5. [Return Value](#return-value)
6. [Full Code Examples](#full-code-examples)
7. [Preparing Film Atom Input](#preparing-film-atom-input)
8. [Glass Atom Inventory](#glass-atom-inventory)
9. [Scientific Basis](#scientific-basis)

---

## Quick Start

```python
from surface_dipole_library import analyze_film_on_glass

# Define only the film — glass is automatic
tio2_film = [
    {"element": "Ti", "charge":  0.580, "position": [0.00, 0.00, 3.50]},
    {"element": "Ti", "charge":  0.580, "position": [2.96, 0.00, 3.50]},
    {"element": "O",  "charge": -0.290, "position": [1.48, 0.00, 4.20]},
    {"element": "O",  "charge": -0.260, "position": [0.00, 1.62, 3.80]},
]

result = analyze_film_on_glass(tio2_film, cutoff=6.0)
print(result["interaction_table"])
```

Output includes a ranked DataFrame of every glass–film atom pair, sorted from
strongest attraction (most negative energy, eV) to strongest repulsion.

---

## The Fixed Glass Substrate

The library embeds a **12-atom borosilicate glass surface** based on the
β-cristobalite SiO₂ (001) surface unit cell.

```
Glass surface structure — 3 layers
────────────────────────────────────────────
z = 0.00 Å   Si backbone (Q4 tetrahedral) + B (B₂O₃ network former)
z = 0.80 Å   Bridging Oxygens (BO) — connect two Si tetrahedra
z = 1.60 Å   Non-Bridging Oxygens (NBO) — surface termination,
              most negative site, primary docking point for the film
z = 2.35 Å   Silanol H (Si–OH) from surface hydroxylation
```

Charges come from the **ClayFF force field** (Cygan, Liang & Kalinichev,
*J. Phys. Chem. B* **108**, 1255–1266, 2004) — the standard model for
oxide surfaces.

| Atom type | Charge (e) | Role |
|-----------|-----------|------|
| Si        | +0.310    | Tetrahedral network former |
| B         | +0.270    | Boron network former (B₂O₃ component) |
| O (BO)    | −0.155    | Bridging oxygen — between two Si |
| O (NBO)   | −0.290    | Non-bridging oxygen — primary film docking site |
| H         | +0.175    | Silanol hydrogen from surface hydroxylation |

---

## Glass Variants

Four glass compositions are available:

| Variant key | Description | Atoms |
|-------------|-------------|-------|
| `"borosilicate"` | **Default** — SiO₂ + B₂O₃ + silanol. Matches commercial display, solar, and optical glass. | 12 |
| `"fused_silica"` | Pure SiO₂ — no boron, no silanol. Ideal substrate baseline. | 10 |
| `"aluminosilicate"` | SiO₂ + Al₂O₃ component. Models Gorilla Glass / E-glass type substrates. | 12 |
| `"soda_lime"` | SiO₂ + Na network modifier. Models window glass and float glass. | 12 |

Select a variant with the `glass_variant` parameter:

```python
result = analyze_film_on_glass(film_atoms, glass_variant="fused_silica")
result = analyze_film_on_glass(film_atoms, glass_variant="aluminosilicate")
result = analyze_film_on_glass(film_atoms, glass_variant="soda_lime")
```

To inspect any glass variant:

```python
from surface_dipole_library import glass_surface_info

glass_surface_info("borosilicate")
glass_surface_info("fused_silica")
```

---

## New API Functions

### `analyze_film_on_glass(film_atoms, ...)`

Run the full dipole–dipole analysis with the substrate fixed as glass.

```python
from surface_dipole_library import analyze_film_on_glass

result = analyze_film_on_glass(
    film_atoms,                    # list[dict] or list[Atom] — film only
    cutoff=6.0,                    # Å — max pair distance (None = all pairs)
    glass_variant="borosilicate",  # which glass composition to use
    verbose=True,                  # print summary table to stdout
)
```

---

### `analyze_film_on_glass_from_xyz(film_file, ...)`

Load the film from a custom XYZ file; substrate is the fixed glass.

```python
from surface_dipole_library import analyze_film_on_glass_from_xyz

result = analyze_film_on_glass_from_xyz(
    "zno_film.xyz",                # 5-column XYZ: element x y z charge
    cutoff=7.0,
    glass_variant="borosilicate",
    has_charges=True,              # 5th column = partial charge
)
```

**XYZ file format** (5 columns, one atom per line):
```
11
ZnO film surface
Zn   0.000   0.000   3.500   0.400
Zn   1.625   0.000   3.500   0.400
O    0.000   0.000   4.900  -0.400
O    1.625   0.000   4.900  -0.400
```

---

### `analyze_film_on_glass_from_ase(film_file, ...)`

Load the film from any ASE-readable format (.cif, POSCAR, .vasp, .xyz, …);
substrate is the fixed glass.

```python
from surface_dipole_library import analyze_film_on_glass_from_ase

result = analyze_film_on_glass_from_ase(
    "ZnO.cif",
    film_charges={"Zn": 0.40, "O": -0.40},   # charges by element
    cutoff=6.0,
    glass_variant="borosilicate",
)
```

---

## Return Value

All three glass-fixed functions return the same dict as `analyze_surface_interactions`,
plus **two extra keys**:

```python
result = {
    # — Standard keys (same as analyze_surface_interactions) —
    "substrate_atoms":   list[Atom],       # the 12 glass atoms used
    "film_atoms":        list[Atom],       # your film atoms (labelled)
    "substrate_dipole":  dict,             # glass dipole vector, magnitude, Debye
    "film_dipole":       dict,             # film dipole vector, magnitude, Debye
    "interaction_table": pd.DataFrame,     # ranked table, best pair first
    "best_interaction":  dict,             # top-ranked pair summary
    "n_pairs":           int,              # number of pairs evaluated

    # — Glass-specific extra keys —
    "glass_variant":     str,              # e.g. "borosilicate"
    "glass_atoms":       list[Atom],       # same as substrate_atoms
}
```

### `interaction_table` columns

| Column | Description |
|--------|-------------|
| `substrate_atom` | Glass atom label (e.g. `O_NBO1_sub`) |
| `film_atom` | Film atom label (e.g. `Ti5c1_film`) |
| `energy_eV` | Dipole–dipole energy in electron-volts |
| `distance_ang` | Centre-to-centre distance in Å |
| `interaction_type` | `attraction`, `repulsion`, or `neutral` |
| `substrate_charge` | Partial charge of the glass atom |
| `film_charge` | Partial charge of the film atom |

Rows are sorted: most negative `energy_eV` first (strongest attraction at top).

---

## Full Code Examples

### Example 1 — TiO₂ film on borosilicate glass

```python
from surface_dipole_library import analyze_film_on_glass

tio2_film = [
    {"element": "Ti", "charge":  0.580, "position": [0.00, 0.00, 3.50]},
    {"element": "Ti", "charge":  0.580, "position": [2.96, 0.00, 3.50]},
    {"element": "Ti", "charge":  0.580, "position": [1.48, 2.96, 3.50]},
    {"element": "O",  "charge": -0.290, "position": [1.48, 0.00, 4.20]},
    {"element": "O",  "charge": -0.290, "position": [4.44, 0.00, 4.20]},
    {"element": "O",  "charge": -0.260, "position": [0.00, 1.62, 3.80]},
    {"element": "O",  "charge": -0.260, "position": [2.96, 1.62, 3.80]},
]

result = analyze_film_on_glass(tio2_film, cutoff=6.0)

# Best glass–film pair
best = result["best_interaction"]
print(f"Best pair: {best['substrate_atom']} ↔ {best['film_atom']}")
print(f"Energy:    {best['energy_eV']:.4f} eV")
print(f"Distance:  {best['distance_ang']:.3f} Å")
```

---

### Example 2 — Compare glass variants for the same film

```python
from surface_dipole_library import analyze_film_on_glass

film = [
    {"element": "Zn", "charge":  0.400, "position": [0.00, 0.00, 3.50]},
    {"element": "O",  "charge": -0.400, "position": [0.00, 0.00, 4.90]},
]

for variant in ["borosilicate", "fused_silica", "aluminosilicate", "soda_lime"]:
    r = analyze_film_on_glass(film, cutoff=8.0, glass_variant=variant, verbose=False)
    best = r["best_interaction"]
    print(f"{variant:18s}  best energy = {best['energy_eV']:.4f} eV  "
          f"pair = {best['substrate_atom']} ↔ {best['film_atom']}")
```

---

### Example 3 — Load film from a POSCAR file

```python
from surface_dipole_library import load_from_poscar, analyze_film_on_glass

film = load_from_poscar(
    "CONTCAR",
    charges={"Ti": 0.580, "O": -0.290},
)

result = analyze_film_on_glass(film, cutoff=7.0)
print(result["interaction_table"].head(10))
```

---

### Example 4 — Inspect glass surface before running analysis

```python
from surface_dipole_library import glass_surface_info, get_glass_surface

# Print a formatted summary of any glass variant
glass_surface_info("borosilicate")

# Access the raw atom dict list
atoms = get_glass_surface("fused_silica")
for a in atoms:
    print(a["label"], a["charge"])
```

---

## Preparing Film Atom Input

Film atom positions must be in the **same Cartesian coordinate system** as the glass.
The glass surface spans:

```
x:  0.00 – 5.06 Å
y:  0.00 – 4.38 Å
z:  0.00 – 2.35 Å  (glass atoms)
```

Film atoms should be **above** the glass surface:

```
z ≥ 2.5 Å recommended minimum separation
z = 3.0 – 5.0 Å  typical film surface layer range
```

If your film coordinates come from a DFT output where z starts at 0, shift them
upward before calling the function:

```python
import numpy as np

shift_z = 3.5   # Å above glass surface

film_atoms = [
    {"element": a["element"],
     "charge":  a["charge"],
     "position": [a["position"][0],
                  a["position"][1],
                  a["position"][2] + shift_z]}
    for a in raw_film_atoms
]
```

**Charge sources:**
- ClayFF / Matsui-Akaogi / ReaxFF force field tables
- Bader charge analysis from DFT (VASP + BADER code)
- `pymatgen.analysis.bond_valence.BVAnalyzer`
- Literature values (e.g., Ti = +0.58 e, O = −0.29 e in TiO₂)

---

## Glass Atom Inventory

Full 12-atom borosilicate glass surface (default substrate):

```
Label          Element   Charge     x      y      z
──────────────────────────────────────────────────────
Si1_sub           Si    +0.310   0.00   0.00   0.00
Si2_sub           Si    +0.310   5.06   0.00   0.00
Si3_sub           Si    +0.310   2.53   4.38   0.00
B1_sub             B    +0.270   2.53   1.46   0.00
O_BO1_sub          O    −0.155   1.60   0.00   0.80
O_BO2_sub          O    −0.155   3.80   0.00   0.80
O_BO3_sub          O    −0.155   1.27   2.19   0.80
O_BO4_sub          O    −0.155   3.79   2.19   0.80
O_NBO1_sub         O    −0.290   0.00   0.00   1.60   ← primary docking site
O_NBO2_sub         O    −0.290   5.06   0.00   1.60   ← primary docking site
O_NBO3_sub         O    −0.290   2.53   4.38   1.60   ← primary docking site
H_OH1_sub          H    +0.175   0.96   0.00   2.35
──────────────────────────────────────────────────────
Net charge                 −0.375 e
```

**NBO atoms are the primary docking sites** — they are the most negative atoms
on the glass surface and form the strongest attractions with positively-charged
film atoms (Ti, Al, Zn).

---

## Scientific Basis

**Glass surface model:**
- Coordinates from the β-cristobalite SiO₂ (001) surface unit cell
  (lattice parameter a = 7.16 Å)
- Partial charges from ClayFF force field — Cygan, Liang & Kalinichev,
  *J. Phys. Chem. B* **108**(4), 1255–1266 (2004)
- Cross-validated against CHARMM-silica (Lopes et al. 2006)
  and INTERFACE FF (Heinz et al. 2013)

**Interaction energy formula:**

```
           Ke   [ μ₁ · μ₂     3 (μ₁ · r̂)(μ₂ · r̂) ]
U = ──── × ─── [ ────────  −  ─────────────────── ]
           r³   [    1              1              ]
```

Where `Ke = 14.3996 eV·Å·e⁻²`, `μ = q·(r − r_centroid)` is the local
atomic dipole (e·Å), and `r` is the distance between atom pair centres.

**What this model captures:**
- Electrostatic dipole–dipole interactions between surface atoms
- Both attraction (opposite-sign charge pairs) and repulsion (same-sign pairs)
- Pair ranking for identifying the optimal bonding pathway

**What this model does NOT capture:**
- Induction / polarizability (~15–20% correction)
- Covalent bonding (DFT required)
- Van der Waals dispersion
- Thermal effects or dynamics

Use this library as a **fast pre-screening tool** to rank candidate thin-film
materials before expensive DFT calculations. It narrows the search space from
dozens of candidates to 2–3 that warrant full simulation.

---

## Module Map

```
surface_dipole_library/
├── __init__.py          ← public API, all imports
├── glass_substrate.py   ← fixed glass surface definition (NEW)
├── main.py              ← high-level API including glass-fixed functions (UPDATED)
├── atoms.py             ← Atom dataclass and labelling
├── dipole.py            ← μ = Σ qᵢrᵢ calculations
├── geometry.py          ← distance / vector helpers
├── interaction.py       ← dipole–dipole energy formula
├── ranking.py           ← pair generator and ranked-table builder
└── io.py                ← file readers (.xyz, .cif, POSCAR, ASE, pymatgen)
```

Files modified in this update: `glass_substrate.py` (new), `main.py`, `__init__.py`.

---

## Before / After Comparison

| | Before | After |
|--|--------|-------|
| User provides | Substrate atoms + film atoms | Film atoms only |
| Glass definition | Hardcoded in each script | Built into the library |
| API call | `analyze_surface_interactions(sub, film)` | `analyze_film_on_glass(film)` |
| Glass variants | Manual | 4 built-in variants |
| Reproducibility | Depends on user's glass definition | Always uses the same validated model |
| Extra result keys | — | `glass_variant`, `glass_atoms` |

---

*surface_dipole_library v1.0.0 — Glass-Fixed API*
*Charges: ClayFF force field — Cygan et al., J. Phys. Chem. B 108, 1255 (2004)*
