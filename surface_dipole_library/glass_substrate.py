"""
glass_substrate.py
------------------
Fixed borosilicate glass surface definition for the surface_dipole_library.

The substrate is locked to the standard SiO2-rich borosilicate glass
surface (representative of commercial display glass, solar-cell cover
glass, and optical glass).  The user only needs to supply the thin film.

Scientific basis
~~~~~~~~~~~~~~~~
Coordinates  : derived from the β-cristobalite SiO₂ surface unit cell
               (lattice parameter a = 7.16 Å, (001) orientation).
Partial charges: ClayFF force field — Cygan, Liang & Kalinichev,
               J. Phys. Chem. B 108(4), 1255–1266 (2004).
               Cross-validated against CHARMM-silica (Lopes et al. 2006)
               and INTERFACE FF (Heinz et al. 2013).

Glass atom inventory (12 atoms, 3 layers)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Layer z = 0.00 Å  — Si backbone (Q4 tetrahedral) + B (B₂O₃ component)
Layer z = 0.80 Å  — Bridging Oxygens (BO) connecting two Si tetrahedra
Layer z = 1.60 Å  — Non-Bridging Oxygens (NBO) — surface-terminating,
                    most negative, primary docking site for the film
Layer z = 2.35 Å  — Silanol H (Si–OH) from moisture-induced hydroxylation

Public API
~~~~~~~~~~
    BOROSILICATE_GLASS_SURFACE  – list[dict], canonical 12-atom definition
    get_glass_surface()         – returns a fresh copy of the atom list
    get_glass_atoms()           – returns list[Atom] (labelled, ready to use)
    glass_surface_info()        – prints a human-readable summary
    GLASS_VARIANTS              – dict of alternate glass compositions
    get_glass_variant(name)     – return a specific glass variant
"""

from __future__ import annotations

import copy
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Canonical borosilicate glass surface — 12 atoms
# ---------------------------------------------------------------------------

BOROSILICATE_GLASS_SURFACE: List[Dict] = [
    # ── Si backbone (Q4 tetrahedral environment) ─────────────────────────
    # Three Si atoms tile the surface in a triangular arrangement.
    # Si–Si distance ≈ 5.06 Å (from β-cristobalite lattice).
    # Charge +0.310 e from ClayFF (Si retains 3.69 of 4 valence electrons).
    {"element": "Si", "charge":  0.310, "position": [0.00, 0.00, 0.00], "label": "Si1_sub"},
    {"element": "Si", "charge":  0.310, "position": [5.06, 0.00, 0.00], "label": "Si2_sub"},
    {"element": "Si", "charge":  0.310, "position": [2.53, 4.38, 0.00], "label": "Si3_sub"},

    # ── Bridging Oxygens (BO) — z = 0.80 Å ──────────────────────────────
    # Each BO bridges two Si tetrahedra.  Position = midpoint between two
    # Si atoms, elevated 0.80 Å in z (Si–O bond projection).
    # Charge −0.155 e = 0.310 / 2  (Si's donated charge split across 2 BO).
    {"element": "O",  "charge": -0.155, "position": [1.60, 0.00, 0.80], "label": "O_BO1_sub"},
    {"element": "O",  "charge": -0.155, "position": [3.80, 0.00, 0.80], "label": "O_BO2_sub"},
    {"element": "O",  "charge": -0.155, "position": [1.27, 2.19, 0.80], "label": "O_BO3_sub"},
    {"element": "O",  "charge": -0.155, "position": [3.79, 2.19, 0.80], "label": "O_BO4_sub"},

    # ── Non-Bridging Oxygens (NBO) — z = 1.60 Å ─────────────────────────
    # Each NBO is bonded to only ONE Si — the other bond is broken at the
    # surface.  Sits directly above its parent Si at z = 1.60 Å (Si–O bond
    # length).  Most negative atom on the glass → primary docking site.
    # Charge −0.290 e (more negative than BO because no second Si to share).
    {"element": "O",  "charge": -0.290, "position": [0.00, 0.00, 1.60], "label": "O_NBO1_sub"},
    {"element": "O",  "charge": -0.290, "position": [5.06, 0.00, 1.60], "label": "O_NBO2_sub"},
    {"element": "O",  "charge": -0.290, "position": [2.53, 4.38, 1.60], "label": "O_NBO3_sub"},

    # ── Boron (B₂O₃ network former) — z = 0.00 Å ────────────────────────
    # B substitutes for Si in borosilicate glass (typically 5–15 mol% B₂O₃).
    # B–O bond = 1.37 Å (shorter than Si–O = 1.62 Å).
    # Charge +0.270 e from CHARMM-silica / ClayFF boron parameter.
    {"element": "B",  "charge":  0.270, "position": [2.53, 1.46, 0.00], "label": "B1_sub"},

    # ── Silanol hydrogen (Si–OH) — z = 2.35 Å ───────────────────────────
    # Surface NBO reacts with atmospheric moisture to form Si–OH (silanol).
    # H sits 0.96 Å from O_NBO1, displaced in x to give correct Si–O–H angle.
    # Charge +0.175 e from ClayFF hydroxyl parameter.
    {"element": "H",  "charge":  0.175, "position": [0.96, 0.00, 2.35], "label": "H_OH1_sub"},
]


# ---------------------------------------------------------------------------
# Alternate glass compositions
# ---------------------------------------------------------------------------

# Pure SiO2 (fused silica) — no boron, no silanol
_FUSED_SILICA: List[Dict] = [
    {"element": "Si", "charge":  0.310, "position": [0.00, 0.00, 0.00], "label": "Si1_sub"},
    {"element": "Si", "charge":  0.310, "position": [5.06, 0.00, 0.00], "label": "Si2_sub"},
    {"element": "Si", "charge":  0.310, "position": [2.53, 4.38, 0.00], "label": "Si3_sub"},
    {"element": "O",  "charge": -0.155, "position": [1.60, 0.00, 0.80], "label": "O_BO1_sub"},
    {"element": "O",  "charge": -0.155, "position": [3.80, 0.00, 0.80], "label": "O_BO2_sub"},
    {"element": "O",  "charge": -0.155, "position": [1.27, 2.19, 0.80], "label": "O_BO3_sub"},
    {"element": "O",  "charge": -0.155, "position": [3.79, 2.19, 0.80], "label": "O_BO4_sub"},
    {"element": "O",  "charge": -0.290, "position": [0.00, 0.00, 1.60], "label": "O_NBO1_sub"},
    {"element": "O",  "charge": -0.290, "position": [5.06, 0.00, 1.60], "label": "O_NBO2_sub"},
    {"element": "O",  "charge": -0.290, "position": [2.53, 4.38, 1.60], "label": "O_NBO3_sub"},
]

# Aluminosilicate glass — Al replaces some Si
_ALUMINOSILICATE: List[Dict] = [
    {"element": "Si", "charge":  0.310, "position": [0.00, 0.00, 0.00], "label": "Si1_sub"},
    {"element": "Al", "charge":  0.480, "position": [5.06, 0.00, 0.00], "label": "Al1_sub"},
    {"element": "Si", "charge":  0.310, "position": [2.53, 4.38, 0.00], "label": "Si2_sub"},
    {"element": "O",  "charge": -0.155, "position": [1.60, 0.00, 0.80], "label": "O_BO1_sub"},
    {"element": "O",  "charge": -0.155, "position": [3.80, 0.00, 0.80], "label": "O_BO2_sub"},
    {"element": "O",  "charge": -0.155, "position": [1.27, 2.19, 0.80], "label": "O_BO3_sub"},
    {"element": "O",  "charge": -0.155, "position": [3.79, 2.19, 0.80], "label": "O_BO4_sub"},
    {"element": "O",  "charge": -0.290, "position": [0.00, 0.00, 1.60], "label": "O_NBO1_sub"},
    {"element": "O",  "charge": -0.290, "position": [5.06, 0.00, 1.60], "label": "O_NBO2_sub"},
    {"element": "O",  "charge": -0.290, "position": [2.53, 4.38, 1.60], "label": "O_NBO3_sub"},
    {"element": "B",  "charge":  0.270, "position": [2.53, 1.46, 0.00], "label": "B1_sub"},
    {"element": "H",  "charge":  0.175, "position": [0.96, 0.00, 2.35], "label": "H_OH1_sub"},
]

# Soda-lime glass — Na included as network modifier
_SODA_LIME: List[Dict] = [
    {"element": "Si", "charge":  0.310, "position": [0.00, 0.00, 0.00], "label": "Si1_sub"},
    {"element": "Si", "charge":  0.310, "position": [5.06, 0.00, 0.00], "label": "Si2_sub"},
    {"element": "Si", "charge":  0.310, "position": [2.53, 4.38, 0.00], "label": "Si3_sub"},
    {"element": "Na", "charge":  0.130, "position": [1.48, 1.48, 0.00], "label": "Na1_sub"},
    {"element": "O",  "charge": -0.155, "position": [1.60, 0.00, 0.80], "label": "O_BO1_sub"},
    {"element": "O",  "charge": -0.155, "position": [3.80, 0.00, 0.80], "label": "O_BO2_sub"},
    {"element": "O",  "charge": -0.155, "position": [1.27, 2.19, 0.80], "label": "O_BO3_sub"},
    {"element": "O",  "charge": -0.155, "position": [3.79, 2.19, 0.80], "label": "O_BO4_sub"},
    {"element": "O",  "charge": -0.290, "position": [0.00, 0.00, 1.60], "label": "O_NBO1_sub"},
    {"element": "O",  "charge": -0.290, "position": [5.06, 0.00, 1.60], "label": "O_NBO2_sub"},
    {"element": "O",  "charge": -0.290, "position": [2.53, 4.38, 1.60], "label": "O_NBO3_sub"},
    {"element": "H",  "charge":  0.175, "position": [0.96, 0.00, 2.35], "label": "H_OH1_sub"},
]

GLASS_VARIANTS: Dict[str, List[Dict]] = {
    "borosilicate":   BOROSILICATE_GLASS_SURFACE,   # default
    "fused_silica":   _FUSED_SILICA,
    "aluminosilicate": _ALUMINOSILICATE,
    "soda_lime":      _SODA_LIME,
}


# ---------------------------------------------------------------------------
# Public helper functions
# ---------------------------------------------------------------------------

def get_glass_surface(variant: str = "borosilicate") -> List[Dict]:
    """
    Return a fresh copy of the fixed glass surface atom list.

    Parameters
    ----------
    variant : str
        One of ``"borosilicate"`` (default), ``"fused_silica"``,
        ``"aluminosilicate"``, ``"soda_lime"``.

    Returns
    -------
    list[dict]
        Deep copy of the atom dict list — safe to modify without
        affecting the library's internal definition.

    Examples
    --------
    >>> from surface_dipole_library import get_glass_surface
    >>> glass = get_glass_surface()          # borosilicate (default)
    >>> silica = get_glass_surface("fused_silica")
    """
    if variant not in GLASS_VARIANTS:
        raise ValueError(
            f"Unknown glass variant '{variant}'. "
            f"Available: {list(GLASS_VARIANTS.keys())}"
        )
    return copy.deepcopy(GLASS_VARIANTS[variant])


def get_glass_atoms(variant: str = "borosilicate"):
    """
    Return the glass surface as a list of :class:`~surface_dipole_library.atoms.Atom`
    objects, fully labelled and ready to pass directly into
    the interaction engine.

    Parameters
    ----------
    variant : str
        Glass composition — see :func:`get_glass_surface`.

    Returns
    -------
    list[Atom]
    """
    from .io import load_from_dict_list
    return load_from_dict_list(get_glass_surface(variant), prefix="sub_")


def glass_surface_info(variant: str = "borosilicate") -> None:
    """
    Print a human-readable summary of the fixed glass substrate.

    Parameters
    ----------
    variant : str
        Glass composition.
    """
    atoms = get_glass_surface(variant)
    print(f"\n{'='*60}")
    print(f"  Fixed Glass Substrate — {variant.replace('_', ' ').title()}")
    print(f"{'='*60}")
    print(f"  Atoms : {len(atoms)}")
    net_q = sum(a['charge'] for a in atoms)
    print(f"  Net Q : {net_q:+.4f} e")
    print(f"\n  {'Label':<18s}  {'Element':>7s}  {'Charge':>8s}  "
          f"{'x':>6s}  {'y':>6s}  {'z':>6s}")
    print(f"  {'-'*58}")
    for a in atoms:
        p = a['position']
        print(f"  {a['label']:<18s}  {a['element']:>7s}  "
              f"{a['charge']:>+8.3f} e  "
              f"{p[0]:>6.2f}  {p[1]:>6.2f}  {p[2]:>6.2f}")
    print(f"\n  Source: ClayFF force field — Cygan et al., "
          f"J. Phys. Chem. B 108, 1255 (2004)")
    print(f"  Variant descriptions:")
    for k in GLASS_VARIANTS:
        mark = " ← selected" if k == variant else ""
        print(f"    '{k}'{mark}")
    print()
