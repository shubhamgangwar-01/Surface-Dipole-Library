# Input Guide — Using the Library with Any New Material

This document answers two questions for anyone bringing a new substrate and
thin film to this library:

1. **What information do I need to provide?**
2. **Where do I get that information from?**

---

## What the Library Needs (Minimum Required Input)

For every atom on both surfaces you need exactly **three things**:

```
┌─────────────────────────────────────────────────────────────────┐
│  Per atom:                                                      │
│                                                                 │
│  1. Element symbol     e.g.  "Si", "Ti", "O", "Al", "Zn"       │
│  2. 3D position        e.g.  [x, y, z]  in Ångströms           │
│  3. Partial charge     e.g.  +0.31, -0.29  in units of e       │
└─────────────────────────────────────────────────────────────────┘
```

Everything else (labels, interaction cutoff) is optional.

In Python this looks like:

```python
substrate_atoms = [
    {"element": "Al", "charge":  0.48, "position": [0.00, 0.00, 0.00], "label": "Al1_sub"},
    {"element": "O",  "charge": -0.32, "position": [1.90, 0.00, 1.20], "label": "O1_sub"},
    ...
]

film_atoms = [
    {"element": "Zn", "charge":  0.40, "position": [0.00, 0.00, 3.50], "label": "Zn1_film"},
    {"element": "O",  "charge": -0.40, "position": [0.00, 0.00, 5.00], "label": "O1_film"},
    ...
]
```

Or loaded from a file:

```python
from surface_dipole_library import load_from_cif, load_from_poscar, load_from_xyz

substrate_atoms = load_from_cif("Al2O3.cif",  charges={"Al": 0.48, "O": -0.32})
film_atoms      = load_from_poscar("CONTCAR", charges={"Zn": 0.40, "O": -0.40})
```

---

## Information 1 — 3D Atomic Positions

### What it is

A list of (x, y, z) coordinates in **Ångströms** for every atom in the
surface layer of each material.

### How to get it

#### Option A — Download a crystal structure (fastest, ~5 minutes)

1. Go to **[Materials Project](https://materialsproject.org)**
2. Search for your material (e.g. "Al2O3", "ZnO", "SnO2")
3. Click the structure → **Download** → choose **CIF** format
4. Open in **VESTA** (free software):
   - `File → Open` the CIF
   - `Objects → Boundary` → set the Miller index of the surface plane
     you want (e.g. (0001) for Al₂O₃ c-plane, (110) for rutile)
   - `Edit → Add vacuum layer` → set 15–20 Å vacuum above the surface
   - `File → Export Data` → save as **POSCAR** or **XYZ**
5. Load the exported file into the library

#### Option B — Build the slab in Python with ASE (reproducible)

```python
from ase.build import surface, bulk, add_vacuum
from ase.io import write

# Step 1: build the bulk unit cell
al2o3 = bulk("Al2O3", crystalstructure="corundum", a=4.76, c=12.99)

# Step 2: cut the surface you want (Miller index, number of layers)
slab = surface(al2o3, (0, 0, 0, 1), layers=4)
add_vacuum(slab, 15.0)   # 15 Å vacuum

# Step 3: export
write("Al2O3_0001.vasp", slab)
```

#### Option C — Run a DFT relaxation (most accurate, for publications)

```
1. Build the initial slab (Option A or B)
2. Run VASP / Quantum ESPRESSO to relax (ionic positions only,
   keep cell fixed for a surface calculation)
3. Use the final geometry (CONTCAR in VASP, output.xyz in QE)
   as your position input — these are the true equilibrium coordinates
```

#### Which surface layer atoms to keep

A slab has many atomic layers — only the **top 1–2 layers** are the actual
surface. Filter by z-coordinate after loading:

```python
from surface_dipole_library import load_from_poscar

all_atoms   = load_from_poscar("CONTCAR", charges={"Al": 0.48, "O": -0.32})
z_max       = max(a.position[2] for a in all_atoms)
surface_atoms = [a for a in all_atoms if a.position[2] >= z_max - 3.0]
```

Adjust the `3.0` cutoff to match your interlayer spacing (typically 1.5–3 Å
for most oxides).

---

## Information 2 — Partial Charges

### What it is

A fractional charge (in units of the electron charge **e**) assigned to each
atom, representing how electron density is redistributed in the real material.
This is **not** the formal oxidation state — it is a softer, partial value.

Typical ranges:

| Element role | Typical partial charge |
|-------------|----------------------|
| Metal cation (Si, Al, Ti, Zn) | +0.2 to +0.8 e |
| Bridging oxygen | −0.1 to −0.2 e |
| Non-bridging / surface oxygen | −0.25 to −0.40 e |
| Surface hydroxyl H | +0.1 to +0.2 e |

### How to get it

#### Option A — Published force-field tables (fastest, good accuracy)

Look up the force field developed for your specific material pair. These are
peer-reviewed and validated against experiments.

| Material | Force Field | Where to find |
|----------|------------|---------------|
| SiO₂, glass | ClayFF / BKS | Cygan et al., J. Phys. Chem. B 108 (2004) |
| Al₂O₃ | INTERFACE FF | Heinz et al., Langmuir 29 (2013) |
| TiO₂ | Matsui–Akaogi | Matsui & Akaogi, Mol. Simul. 6 (1991) |
| ZnO | Buckingham | Lewis & Catlow, J. Phys. C 18 (1985) |
| SnO₂ | ReaxFF | Kim et al., J. Phys. Chem. C 117 (2013) |
| Fe₂O₃ | CLAYFF | Zeitler et al., J. Phys. Chem. C 116 (2012) |
| General oxides | UFF / DREIDING | Rappe et al., JACS 114 (1992) |

**Quick lookup approach:**
Search Google Scholar for:  `"[your material]" "partial charge" "force field"`

#### Option B — DFT Bader charge analysis (most accurate)

Run a single-point DFT calculation and extract charges from the electron
density:

```
Software:  VASP + bader.exe (free from theory.cm.utexas.edu/henkelman/code)

Steps:
1. Run VASP with LAECHG = .TRUE. (writes electron density files)
2. Run:  bader CHGCAR -ref AECCAR0 -ref AECCAR2
3. Output:  ACF.dat — column 5 is the Bader charge per atom
4. Partial charge = (valence electrons) − (Bader charge)
   e.g. for O:  formal valence = 6e,  Bader charge = 7.3e
         partial charge = 6 − 7.3 = −1.3 → normalise to −0.33 e by
         dividing by the number of valence electrons you chose
```

For Quantum ESPRESSO:

```
Run projwfc.x → Lowdin charges are printed in projwfc output
```

#### Option C — Pymatgen oxidation state estimator (rough, for quick screening)

```python
from pymatgen.core import Structure
from pymatgen.analysis.bond_valence import BVAnalyzer

structure = Structure.from_file("Al2O3.cif")
bv = BVAnalyzer()
structure = bv.get_oxi_state_decorated_structure(structure)

# Extract charges
charges = {str(site.specie): float(site.specie.oxi_state)
           for site in structure}
print(charges)
# {'Al3+': 3.0, 'O2-': -2.0}  ← integer oxidation states, not partial
```

These are integer oxidation states (Al = +3, O = −2), which are rougher
than DFT partial charges but useful when you have no other data.

---

## Aligning the Two Surfaces in z

The library works in a shared Cartesian coordinate system. When you have two
separate structure files, you need to place them at the right z-separation
before running the analysis.

```python
import numpy as np
from surface_dipole_library import load_from_cif

substrate = load_from_cif("Al2O3.cif",  charges={"Al": 0.48, "O": -0.32})
film      = load_from_cif("ZnO.cif",    charges={"Zn": 0.40, "O": -0.40})

# Find the top of the substrate and bottom of the film
sub_z_max  = max(a.position[2] for a in substrate)
film_z_min = min(a.position[2] for a in film)

# Shift the film so it sits 2.5 Å above the substrate surface
gap    = 2.5   # Å — typical physisorption / van der Waals gap
shift  = sub_z_max + gap - film_z_min

for atom in film:
    atom.position[2] += shift
```

A typical gap between surfaces is **2.0–3.5 Å**, depending on whether you
expect physisorption (2.5–3.5 Å) or chemisorption (1.8–2.5 Å).

---

## Complete Workflow for a New Material Pair

```
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1 — Get the crystal structure                             │
│  → Download CIF from Materials Project                          │
│  → Cut a surface slab in VESTA or ASE                           │
│  → Do this for BOTH substrate and film                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│  STEP 2 — Get partial charges                                   │
│  → Look up the force field for your material (fastest)          │
│  → OR run DFT + Bader analysis (most accurate)                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│  STEP 3 — Load into the library                                 │
│  → load_from_cif() / load_from_poscar() / load_from_xyz()       │
│  → Pass the charges dict                                        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│  STEP 4 — Align the two surfaces in z                           │
│  → Shift film so it sits 2.0–3.5 Å above substrate top         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│  STEP 5 — Run the analysis                                      │
│  from surface_dipole_library import analyze_surface_interactions │
│  result = analyze_surface_interactions(substrate, film,         │
│                                        cutoff=6.0)              │
│  print(result["interaction_table"])                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Accuracy vs. Effort Trade-off

| Positions from | Charges from | Accuracy | Effort |
|---------------|-------------|---------|--------|
| DFT relaxation | DFT Bader | Highest | High |
| DFT relaxation | Published FF | High | Medium |
| VESTA slab (CIF) | Published FF | Good | Low |
| VESTA slab (CIF) | Oxidation states | Rough | Minimal |

For the **primary use case** of this library — pre-screening candidate
interfaces before a full DFT calculation — the third row
(**VESTA slab + published FF charges**) is the recommended starting point.
It takes under an hour and identifies which atom pairs to focus on before
investing compute time in DFT.

---

*surface_dipole_library v1.0.0*
