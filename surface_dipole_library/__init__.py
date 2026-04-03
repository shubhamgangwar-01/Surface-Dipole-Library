"""
surface_dipole_library
======================
A production-ready Python library for calculating dipole moments and
dipole–dipole interaction strengths between surface atoms of a substrate
and a thin film.

Primary use-case: screening glass–thin-film interfaces (SiO₂, borosilicate,
aluminosilicate glass vs. TiO₂, Al₂O₃, ZnO, ITO, Si₃N₄ films) before
expensive DFT simulations.

Quick start
-----------
>>> from surface_dipole_library import analyze_surface_interactions
>>>
>>> substrate_atoms = [
...     {"element": "Si", "charge":  0.30, "position": [0.0, 0.0, 0.0]},
...     {"element": "O",  "charge": -0.15, "position": [1.6, 0.0, 0.0]},
...     {"element": "O",  "charge": -0.15, "position": [0.0, 1.6, 0.0]},
... ]
>>> film_atoms = [
...     {"element": "Ti", "charge":  0.50, "position": [0.0, 0.0, 3.0]},
...     {"element": "O",  "charge": -0.25, "position": [1.6, 0.0, 3.0]},
... ]
>>> result = analyze_surface_interactions(substrate_atoms, film_atoms, cutoff=6.0)
>>> print(result["interaction_table"])

Module map
----------
atoms       – Atom dataclass and labelling utilities
dipole      – Dipole moment calculations (μ = Σ qᵢ rᵢ)
geometry    – Distance and vector helpers
interaction – Dipole–dipole energy formula
ranking     – Pair generator and ranked-table builder
io          – Structure file readers (.xyz, .cif, POSCAR, ASE, pymatgen)
main        – High-level API (analyze_surface_interactions)
"""

__version__ = "1.0.0"
__author__  = "surface_dipole_library contributors"
__license__ = "MIT"

# ---------------------------------------------------------------------------
# Public API – flat imports so users only need ``from surface_dipole_library``
# ---------------------------------------------------------------------------

# Primary entry point
from .main import (
    analyze_surface_interactions,
    analyze_from_xyz,
    analyze_from_ase,
    # Glass-fixed API  — substrate locked to borosilicate glass
    analyze_film_on_glass,
    analyze_film_on_glass_from_xyz,
    analyze_film_on_glass_from_ase,
)

# Fixed glass substrate
from .glass_substrate import (
    BOROSILICATE_GLASS_SURFACE,
    GLASS_VARIANTS,
    get_glass_surface,
    get_glass_atoms,
    glass_surface_info,
)

# Atom class and helpers
from .atoms import (
    Atom,
    atoms_from_dicts,
    assign_labels,
)

# Dipole calculations
from .dipole import (
    calculate_dipole,
    calculate_centroid,
    charge_centroid,
    atomic_local_dipole,
    dipole_summary,
    DEBYE_PER_E_ANG,
)

# Geometry utilities
from .geometry import (
    displacement_vector,
    distance,
    unit_vector,
    angle_between,
    midpoint,
    are_within_cutoff,
    pairwise_distances,
    nearest_neighbours,
)

# Interaction physics
from .interaction import (
    dipole_dipole_energy,
    atom_pair_interaction,
    interaction_type,
    K_E,
    MIN_DISTANCE,
)

# Ranking and table construction
from .ranking import (
    generate_all_pairs,
    rank_interactions,
    best_interaction,
    print_summary,
)

# IO helpers
from .io import (
    load_from_dict_list,
    load_from_xyz,
    load_from_ase,
    load_from_poscar,
    load_from_cif,
    write_xyz,
)

# ---------------------------------------------------------------------------
# __all__ – explicit public surface
# ---------------------------------------------------------------------------

__all__ = [
    # Version
    "__version__",
    # High-level API
    "analyze_surface_interactions",
    "analyze_from_xyz",
    "analyze_from_ase",
    # Glass-fixed API
    "analyze_film_on_glass",
    "analyze_film_on_glass_from_xyz",
    "analyze_film_on_glass_from_ase",
    # Fixed glass substrate
    "BOROSILICATE_GLASS_SURFACE",
    "GLASS_VARIANTS",
    "get_glass_surface",
    "get_glass_atoms",
    "glass_surface_info",
    # Atom
    "Atom",
    "atoms_from_dicts",
    "assign_labels",
    # Dipole
    "calculate_dipole",
    "calculate_centroid",
    "charge_centroid",
    "atomic_local_dipole",
    "dipole_summary",
    "DEBYE_PER_E_ANG",
    # Geometry
    "displacement_vector",
    "distance",
    "unit_vector",
    "angle_between",
    "midpoint",
    "are_within_cutoff",
    "pairwise_distances",
    "nearest_neighbours",
    # Interaction
    "dipole_dipole_energy",
    "atom_pair_interaction",
    "interaction_type",
    "K_E",
    "MIN_DISTANCE",
    # Ranking
    "generate_all_pairs",
    "rank_interactions",
    "best_interaction",
    "print_summary",
    # IO
    "load_from_dict_list",
    "load_from_xyz",
    "load_from_ase",
    "load_from_poscar",
    "load_from_cif",
    "write_xyz",
]
