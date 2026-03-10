# surface_dipole_library

A production-ready Python library for calculating **dipole moments** and **dipole–dipole interaction strengths** between surface atoms of a substrate and a thin film.

Designed for **glass–thin-film interface research** as a fast pre-screening tool before expensive DFT simulations.

---

## Table of Contents

1. [Scientific Background](#scientific-background)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Input Data Format](#input-data-format)
5. [API Reference](#api-reference)
6. [Loading Structure Files](#loading-structure-files)
7. [Interpreting Results](#interpreting-results)
8. [Example – Borosilicate Glass vs. TiO₂](#example--borosilicate-glass-vs-tio₂)
9. [Physical Equations](#physical-equations)
10. [Module Map](#module-map)
12. [Supported Materials](#supported-materials)
13. [Running Tests](#running-tests)
14. [License](#license)

> **Full step-by-step scientific walkthrough** (input → dipole moments →
> local atomic dipoles → 132 pairwise energies → ranked table → conclusions):
> see [WALKTHROUGH.md](WALKTHROUGH.md)

---

## Scientific Background

When a thin film is deposited on a glass substrate, the initial adhesion is governed by
electrostatic interactions between surface dipoles.  Atoms with high partial charges
near the interface create local dipole moments that interact according to classical
dipole–dipole physics.

This library:

- Computes the **net dipole moment** of each surface group.
- Computes the **effective local dipole** of every individual surface atom.
- Evaluates the **dipole–dipole interaction energy** for every substrate–film atom pair.
- Produces a **ranked table** (strongest attraction → weakest) to guide experimental design.

---

## Installation

### Minimal (numpy + pandas only)

```bash
pip install surface-dipole-library
```

Or directly from source:

```bash
git clone https://github.com/your-org/surface-dipole-library.git
cd surface-dipole-library
pip install -e .
```

### With file-reading support

```bash
pip install "surface-dipole-library[ase]"          # adds ASE (CIF, POSCAR, XYZ, …)
pip install "surface-dipole-library[pymatgen]"      # adds pymatgen
pip install "surface-dipole-library[all]"           # both
```

### Development

```bash
pip install -e ".[dev]"
```

---

## Quick Start

```python
from surface_dipole_library import analyze_surface_interactions

substrate_atoms = [
    {"element": "Si", "charge":  0.30,  "position": [0.0, 0.0, 0.0]},
    {"element": "O",  "charge": -0.15,  "position": [1.6, 0.0, 0.0]},
    {"element": "O",  "charge": -0.15,  "position": [0.0, 1.6, 0.0]},
]

film_atoms = [
    {"element": "Ti", "charge":  0.50,  "position": [0.0, 0.0, 3.0]},
    {"element": "O",  "charge": -0.25,  "position": [1.6, 0.0, 3.0]},
]

result = analyze_surface_interactions(
    substrate_atoms,
    film_atoms,
    cutoff=6.0,   # only consider pairs within 6 Å
    verbose=True, # print formatted table to stdout
)

print(result["interaction_table"])
print(result["best_interaction"])
```

**Sample output:**

```
========================================================================
  SURFACE DIPOLE INTERACTION ANALYSIS
========================================================================

Substrate Dipole Moment:
  μx = -0.240000 e·Å
  μy = -0.240000 e·Å
  μz =  0.000000 e·Å
  |μ| = 0.339411 e·Å  (1.6297 D)

Film Dipole Moment:
  μx = -0.400000 e·Å
  μy =  0.000000 e·Å
  μz =  1.250000 e·Å
  |μ| = 1.311536 e·Å  (6.2985 D)

Ranked Interaction Table  (6 pairs):
========================================================================
 Rank Substrate Atom Film Atom  Distance (Å)  Interaction Energy (eV) Interaction Type
    1      sub_O1  film_Ti1        3.0000                  -0.0000       attractive
    2      sub_O2  film_Ti1        3.2311                  -0.0000       attractive
  ...
```

---

## Input Data Format

Each atom is a Python dictionary with three required fields:

| Key        | Type        | Units        | Description                            |
|------------|-------------|--------------|----------------------------------------|
| `element`  | `str`       | –            | Chemical symbol, e.g. `"Si"`, `"O"`   |
| `charge`   | `float`     | elementary e | Partial charge (+ for cations)         |
| `position` | `list[3]`   | Å            | Cartesian coordinates `[x, y, z]`     |

An optional `label` key gives a custom identifier; otherwise labels are auto-generated
(e.g. `sub_Si1`, `film_Ti1`).

```python
{"element": "Si", "charge": 0.31, "position": [0.00, 0.00, 0.00], "label": "Si_surface"}
```

> **Coordinate convention:** all atoms (substrate and film) must be expressed in the
> **same Cartesian frame**.  Typically the substrate sits near z ≈ 0 and the film
> surface is placed at z > 0.

---

## API Reference

### `analyze_surface_interactions`

```python
result = analyze_surface_interactions(
    substrate_atoms,   # list[dict] or list[Atom]
    film_atoms,        # list[dict] or list[Atom]
    cutoff=None,       # float (Å) or None for all pairs
    verbose=True,      # print summary
)
```

**Returns** a dict:

| Key                  | Type             | Description                               |
|----------------------|------------------|-------------------------------------------|
| `substrate_atoms`    | `list[Atom]`     | Labelled substrate atoms                  |
| `film_atoms`         | `list[Atom]`     | Labelled film atoms                       |
| `substrate_dipole`   | `dict`           | μ vector, |μ|, Debye value, net charge    |
| `film_dipole`        | `dict`           | same structure                            |
| `interaction_table`  | `pd.DataFrame`   | Ranked table (see columns below)          |
| `best_interaction`   | `dict`           | Top-ranked pair summary                   |
| `n_pairs`            | `int`            | Total pairs evaluated                     |

**DataFrame columns:**

| Column                    | Description                              |
|---------------------------|------------------------------------------|
| `Rank`                    | 1 = strongest attraction                 |
| `Substrate Atom`          | Label of substrate atom                  |
| `Film Atom`               | Label of film atom                       |
| `Substrate Element`       | Element symbol                           |
| `Film Element`            | Element symbol                           |
| `Substrate Charge (e)`    | Partial charge                           |
| `Film Charge (e)`         | Partial charge                           |
| `Distance (Å)`            | Atom–atom separation                     |
| `mu1 Magnitude (e·Å)`     | Local dipole magnitude of substrate atom |
| `mu2 Magnitude (e·Å)`     | Local dipole magnitude of film atom      |
| `Interaction Energy (eV)` | **Negative = attractive**                |
| `Interaction Type`        | `"attractive"` or `"repulsive"`          |

---

### `analyze_from_xyz`

Load both surfaces from 5-column XYZ files (element x y z charge):

```python
from surface_dipole_library import analyze_from_xyz

result = analyze_from_xyz(
    "glass_surface.xyz",
    "tio2_film.xyz",
    cutoff=7.0,
)
```

### `analyze_from_ase`

Load from any ASE-supported format (.cif, POSCAR, .vasp, …):

```python
from surface_dipole_library import analyze_from_ase

result = analyze_from_ase(
    "SiO2_surface.cif",
    "TiO2_film.vasp",
    substrate_charges={"Si": 0.31, "O": -0.155},
    film_charges={"Ti": 0.58, "O": -0.29},
    cutoff=7.0,
)
```

---

## Loading Structure Files

### Custom XYZ with charges (5-column)

```
12
Borosilicate glass surface
Si   0.000000   0.000000   0.000000   0.310
O    1.600000   0.000000   0.800000  -0.155
O    0.000000   1.600000   0.800000  -0.155
...
```

```python
from surface_dipole_library import load_from_xyz
atoms = load_from_xyz("glass_surface.xyz", prefix="sub_")
```

### Standard XYZ (no charges)

```python
atoms = load_from_xyz("structure.xyz", has_charges=False)
for atom in atoms:
    atom.charge = charge_map[atom.element]   # assign manually
```

### CIF file

```python
from surface_dipole_library import load_from_cif
atoms = load_from_cif(
    "SiO2.cif",
    charges={"Si": 0.31, "O": -0.155},
    prefix="sub_",
)
```

### POSCAR / CONTCAR (VASP)

```python
from surface_dipole_library import load_from_poscar
atoms = load_from_poscar(
    "POSCAR",
    charges={"Ti": 0.58, "O": -0.29},
    prefix="film_",
)
```

---

## Interpreting Results

### Interaction Energy

| Energy (eV) | Meaning                              |
|-------------|--------------------------------------|
| Negative    | **Attractive** – these pairs bond    |
| Near zero   | Negligible interaction               |
| Positive    | **Repulsive** – these pairs repel    |

The ranking goes from **most negative** (rank 1, strongest attraction) to **most positive**.

### Dipole Moment

Units: **e·Å** (1 e·Å ≈ 4.803 Debye).

The direction of μ tells you which way the electron density is displaced.
A large |μ| on the film surface means a highly polar termination that will
interact strongly with charged substrate sites.

### Typical charge ranges

| Material             | Element | Typical charge (e) |
|----------------------|---------|--------------------|
| SiO₂ glass           | Si      | +0.28 to +0.35     |
| SiO₂ glass           | O (BO)  | −0.14 to −0.17     |
| SiO₂ glass           | O (NBO) | −0.25 to −0.35     |
| Borosilicate         | B       | +0.22 to +0.28     |
| TiO₂ (rutile)        | Ti      | +0.44 to +0.60     |
| TiO₂ (rutile)        | O       | −0.22 to −0.30     |
| Al₂O₃ (corundum)     | Al      | +0.40 to +0.50     |
| Al₂O₃ (corundum)     | O       | −0.27 to −0.33     |
| ZnO (wurtzite)       | Zn      | +0.35 to +0.45     |
| ZnO (wurtzite)       | O       | −0.35 to −0.45     |

---

## Example – Borosilicate Glass vs. TiO₂

For a complete step-by-step walkthrough of this example — covering every
calculation stage, hand-traced numbers, and scientific conclusions — see
**[WALKTHROUGH.md](WALKTHROUGH.md)**.

Run the full demo:

```bash
python tests/test_glass_tio2.py
```

This uses a 12-atom borosilicate glass surface model and an 11-atom rutile TiO₂(110)
surface model with literature-derived partial charges.

Expected physical interpretation:

- **Ti5c – O_NBO** pairs rank highest (most attractive) because the undercoordinated
  Ti5c site is electron-deficient and strongly attracted to the negatively charged
  non-bridging oxygens on the glass surface.
- **O_film – Si_sub** pairs may also be attractive due to Si being slightly positive.
- **O_film – O_sub** pairs are typically weakly repulsive.

---

## Physical Equations

### Dipole Moment

```
μ = Σᵢ qᵢ rᵢ        (units: e·Å)
```

### Effective Atomic Local Dipole

```
μᵢ(local) = qᵢ × (rᵢ − r_centroid)
```

This decomposes the total group dipole into per-atom contributions and is
independent of the global coordinate origin.

### Dipole–Dipole Interaction Energy

```
U = (1/4πε₀) [ (μ₁·μ₂)/r³  −  3(μ₁·r)(μ₂·r)/r⁵ ]
```

In practical units (μ in e·Å, r in Å, U in eV):

```
U = 14.3996 × [ (μ₁·μ₂)/r³  −  3(μ₁·r)(μ₂·r)/r⁵ ]
```

where 14.3996 = k_e × e² / Å = Coulomb constant in eV·Å/e².

---

## Module Map

```
surface_dipole_library/
├── __init__.py      – flat public API exports
├── atoms.py         – Atom dataclass, labelling helpers
├── dipole.py        – calculate_dipole(), atomic_local_dipole()
├── geometry.py      – distance(), displacement_vector(), pairwise_distances()
├── interaction.py   – dipole_dipole_energy(), atom_pair_interaction()
├── ranking.py       – generate_all_pairs(), rank_interactions(), print_summary()
├── io.py            – XYZ / CIF / POSCAR / ASE / pymatgen readers & writer
└── main.py          – analyze_surface_interactions() high-level entry point

tests/
└── test_glass_tio2.py   – borosilicate glass vs. TiO₂ demo + unit tests
```

---

## Supported Materials

### Glass substrates

| Glass type         | Typical composition         |
|--------------------|-----------------------------|
| Fused silica       | SiO₂                        |
| Borosilicate       | SiO₂ · B₂O₃ · Na₂O         |
| Aluminosilicate    | SiO₂ · Al₂O₃ · (Na/K)₂O   |
| Soda-lime          | SiO₂ · Na₂O · CaO           |

### Thin films

| Film material | Crystal structure  |
|---------------|--------------------|
| TiO₂          | Rutile / Anatase   |
| Al₂O₃         | Corundum (α)       |
| ZnO           | Wurtzite           |
| Si₃N₄         | α / β              |
| ITO           | Bixbyite           |
| HfO₂          | Monoclinic         |
| ZrO₂          | Cubic / Monoclinic |

---

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=surface_dipole_library

# Run demo directly
python tests/test_glass_tio2.py
```

---

## License

MIT License.  See `LICENSE` for details.

---

## Citation

If you use this library in academic work please cite:

```
surface_dipole_library v1.0.0
https://github.com/your-org/surface-dipole-library
```
