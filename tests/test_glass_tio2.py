"""
tests/test_glass_tio2.py
------------------------
Example test: SiO2 borosilicate glass surface  vs.  TiO2 thin-film surface.

This script demonstrates the full workflow of the surface_dipole_library and
can be run directly:

    python tests/test_glass_tio2.py

or via pytest:

    pytest tests/test_glass_tio2.py -v

Scientific context
~~~~~~~~~~~~~~~~~~
Glass surface (SiO2 / borosilicate):
    Bridging oxygens (BO) and non-bridging oxygens (NBO) carry negative partial
    charges; Si and B carry positive charges.

TiO2 film (rutile-like surface termination):
    Ti cations carry +0.5 to +0.8 e; surface oxygens carry -0.25 to -0.35 e.
    The undercoordinated Ti5c site is the primary adsorption site.

Expected outcome:
    Ti (positive) – O_NBO (negative) pairs should show the strongest
    attractive (most negative energy) dipole–dipole interactions.
"""

import sys
import os

# Allow running from the repo root without installing the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pandas as pd

from surface_dipole_library import (
    analyze_surface_interactions,
    calculate_dipole,
    dipole_summary,
    distance,
    Atom,
)


# ===========================================================================
# Dataset definitions
# ===========================================================================

# ---------------------------------------------------------------------------
# Borosilicate glass surface atoms (representative SiO2-rich termination)
# Coordinates in Angstroms, charges from force-field literature (ClayFF / CHARMM)
# ---------------------------------------------------------------------------
GLASS_SURFACE = [
    # Tetrahedral Si (Q4 environment)
    {"element": "Si",  "charge":  0.310,  "position": [0.00,  0.00,  0.00], "label": "Si1_sub"},
    {"element": "Si",  "charge":  0.310,  "position": [5.06,  0.00,  0.00], "label": "Si2_sub"},
    {"element": "Si",  "charge":  0.310,  "position": [2.53,  4.38,  0.00], "label": "Si3_sub"},
    # Bridging oxygens (BO) – connect two Si tetrahedra
    {"element": "O",   "charge": -0.155,  "position": [1.60,  0.00,  0.80], "label": "O_BO1_sub"},
    {"element": "O",   "charge": -0.155,  "position": [3.80,  0.00,  0.80], "label": "O_BO2_sub"},
    {"element": "O",   "charge": -0.155,  "position": [1.27,  2.19,  0.80], "label": "O_BO3_sub"},
    {"element": "O",   "charge": -0.155,  "position": [3.79,  2.19,  0.80], "label": "O_BO4_sub"},
    # Non-bridging oxygens (NBO) – terminating the surface, more negative
    {"element": "O",   "charge": -0.290,  "position": [0.00,  0.00,  1.60], "label": "O_NBO1_sub"},
    {"element": "O",   "charge": -0.290,  "position": [5.06,  0.00,  1.60], "label": "O_NBO2_sub"},
    {"element": "O",   "charge": -0.290,  "position": [2.53,  4.38,  1.60], "label": "O_NBO3_sub"},
    # Boron atom (B2O3 component of borosilicate)
    {"element": "B",   "charge":  0.270,  "position": [2.53,  1.46,  0.00], "label": "B1_sub"},
    # Hydroxyl H (surface silanol –OH)
    {"element": "H",   "charge":  0.175,  "position": [0.96,  0.00,  2.35], "label": "H_OH1_sub"},
]

# ---------------------------------------------------------------------------
# TiO2 thin-film surface atoms (rutile (110) termination)
# Standard coordinates shifted +3.5 Å in z above the glass surface top
# Charges from DFT-derived force fields (Matsui-Akaogi / ReaxFF)
# ---------------------------------------------------------------------------
TIO2_FILM = [
    # 5-fold coordinated Ti (Ti5c) – most reactive surface site
    {"element": "Ti",  "charge":  0.580,  "position": [0.00,  0.00,  3.50], "label": "Ti5c1_film"},
    {"element": "Ti",  "charge":  0.580,  "position": [2.96,  0.00,  3.50], "label": "Ti5c2_film"},
    {"element": "Ti",  "charge":  0.580,  "position": [1.48,  3.25,  3.50], "label": "Ti5c3_film"},
    # 6-fold coordinated Ti (Ti6c) – bulk-like
    {"element": "Ti",  "charge":  0.480,  "position": [1.48,  1.48,  4.50], "label": "Ti6c1_film"},
    # Bridging oxygen rows (2-fold coordinated)
    {"element": "O",   "charge": -0.290,  "position": [1.48,  0.00,  4.20], "label": "O_br1_film"},
    {"element": "O",   "charge": -0.290,  "position": [4.44,  0.00,  4.20], "label": "O_br2_film"},
    {"element": "O",   "charge": -0.290,  "position": [2.96,  3.25,  4.20], "label": "O_br3_film"},
    # In-plane oxygens (3-fold coordinated)
    {"element": "O",   "charge": -0.260,  "position": [0.00,  1.62,  3.80], "label": "O_ip1_film"},
    {"element": "O",   "charge": -0.260,  "position": [2.96,  1.62,  3.80], "label": "O_ip2_film"},
    # Surface hydroxyl (adsorbed –OH on Ti5c in humid conditions)
    {"element": "O",   "charge": -0.200,  "position": [0.00,  0.00,  5.20], "label": "O_OH1_film"},
    {"element": "H",   "charge":  0.180,  "position": [0.00,  0.96,  5.80], "label": "H_OH1_film"},
]


# ===========================================================================
# Unit tests (pytest-compatible)
# ===========================================================================


def test_dipole_moments():
    """Dipole vectors are finite and magnitudes are non-negative."""
    from surface_dipole_library import load_from_dict_list

    sub_atoms  = load_from_dict_list(GLASS_SURFACE)
    film_atoms = load_from_dict_list(TIO2_FILM)

    d_sub  = calculate_dipole(sub_atoms)
    d_film = calculate_dipole(film_atoms)

    assert np.isfinite(d_sub["dipole_magnitude"]),  "Substrate dipole is NaN/Inf"
    assert np.isfinite(d_film["dipole_magnitude"]), "Film dipole is NaN/Inf"
    assert d_sub["dipole_magnitude"]  >= 0
    assert d_film["dipole_magnitude"] >= 0

    print("\n[PASS] test_dipole_moments")
    print(dipole_summary(sub_atoms,  "Glass substrate surface"))
    print(dipole_summary(film_atoms, "TiO2 film surface"))


def test_interaction_table_structure():
    """Interaction table has correct columns, no NaN values, is sorted."""
    result = analyze_surface_interactions(
        GLASS_SURFACE, TIO2_FILM, cutoff=8.0, verbose=False
    )
    df = result["interaction_table"]

    required_cols = [
        "Rank", "Substrate Atom", "Film Atom",
        "Substrate Charge (e)", "Film Charge (e)",
        "Distance (Å)", "Interaction Energy (eV)", "Interaction Type",
    ]
    for col in required_cols:
        assert col in df.columns, f"Missing column: {col}"

    assert not df["Interaction Energy (eV)"].isna().any(), "NaN in energy column"
    assert not df["Distance (Å)"].isna().any(),            "NaN in distance column"

    # Verify ascending energy sort (rank 1 = most negative)
    energies = df["Interaction Energy (eV)"].tolist()
    assert energies == sorted(energies), "Table is not sorted by energy"

    # Ranks must be 1-based and contiguous
    assert list(df["Rank"]) == list(range(1, len(df) + 1))

    print(f"\n[PASS] test_interaction_table_structure  ({len(df)} pairs)")


def test_best_interaction_is_attractive():
    """The highest-ranked interaction must be attractive (negative energy)
    given that opposite charges dominate in this glass–TiO2 system."""
    result = analyze_surface_interactions(
        GLASS_SURFACE, TIO2_FILM, cutoff=8.0, verbose=False
    )
    best = result["best_interaction"]

    assert best["interaction_type"] == "attractive", (
        f"Expected attractive best interaction, got {best['interaction_type']} "
        f"(energy={best['energy_eV']:.6f} eV)"
    )
    assert best["energy_eV"] < 0, (
        f"Expected negative energy for best pair, got {best['energy_eV']:.6f} eV"
    )

    print(f"\n[PASS] test_best_interaction_is_attractive")
    print(f"  Best pair : {best['substrate_atom']}  –  {best['film_atom']}")
    print(f"  Energy    = {best['energy_eV']:.6f} eV")
    print(f"  Distance  = {best['distance_ang']:.4f} Å")


def test_distance_calculation():
    """Spot-check the distance function against a known pair."""
    sub  = Atom("O",  charge=-0.29, position=[0.0, 0.0, 1.60])
    film = Atom("Ti", charge=0.58,  position=[0.0, 0.0, 3.50])
    d = distance(sub, film)
    expected = 1.90  # 3.50 - 1.60 = 1.90 Å (purely z-separated)
    assert abs(d - expected) < 1e-6, f"Distance mismatch: {d:.6f} vs {expected:.6f}"
    print(f"\n[PASS] test_distance_calculation  (d={d:.4f} Å)")


def test_cutoff_filter():
    """With a very small cutoff, fewer pairs should survive."""
    result_all = analyze_surface_interactions(
        GLASS_SURFACE, TIO2_FILM, cutoff=None, verbose=False
    )
    result_cut = analyze_surface_interactions(
        GLASS_SURFACE, TIO2_FILM, cutoff=4.5, verbose=False
    )
    assert result_cut["n_pairs"] <= result_all["n_pairs"], (
        "Cutoff did not reduce the number of pairs"
    )
    print(f"\n[PASS] test_cutoff_filter  "
          f"(all={result_all['n_pairs']} pairs, "
          f"cutoff=4.5 Å → {result_cut['n_pairs']} pairs)")


def test_energy_symmetry():
    """Swapping μ1 ↔ μ2 must not change the energy."""
    from surface_dipole_library import dipole_dipole_energy
    rng = np.random.default_rng(42)
    mu1   = rng.uniform(-1, 1, 3)
    mu2   = rng.uniform(-1, 1, 3)
    r_vec = np.array([0.0, 0.0, 3.5])

    e12 = dipole_dipole_energy(mu1, mu2, r_vec)
    e21 = dipole_dipole_energy(mu2, mu1, r_vec)
    assert abs(e12 - e21) < 1e-10, f"Asymmetry: {e12} vs {e21}"
    print(f"\n[PASS] test_energy_symmetry  (U={e12:.8f} eV)")


# ===========================================================================
# Full demonstration run
# ===========================================================================


def run_full_demo():
    """
    Execute the complete analysis and print the ranked interaction table.
    This mirrors what a researcher would run in their script.
    """
    print("\n" + "=" * 72)
    print("  DEMO: Borosilicate Glass  vs.  TiO2 Thin Film")
    print("=" * 72)

    result = analyze_surface_interactions(
        substrate_atoms=GLASS_SURFACE,
        film_atoms=TIO2_FILM,
        cutoff=8.0,
        verbose=True,   # prints formatted summary automatically
    )

    df   = result["interaction_table"]
    best = result["best_interaction"]

    # Show full table
    pd.set_option("display.max_rows",    200)
    pd.set_option("display.max_columns", 20)
    pd.set_option("display.width",       120)
    pd.set_option("display.float_format", "{:.4f}".format)

    print("\nFull Ranked Interaction Table:")
    print(df.to_string(index=False))

    print("\n" + "-" * 72)
    print("Substrate Group Dipole:")
    d_sub = result["substrate_dipole"]
    print(f"  |μ| = {d_sub['dipole_magnitude']:.4f} e·Å  "
          f"({d_sub['dipole_debye']:.3f} D)")
    print(f"  μ = [{d_sub['mu_x']:+.4f}, {d_sub['mu_y']:+.4f}, {d_sub['mu_z']:+.4f}] e·Å")

    print("\nFilm Group Dipole:")
    d_film = result["film_dipole"]
    print(f"  |μ| = {d_film['dipole_magnitude']:.4f} e·Å  "
          f"({d_film['dipole_debye']:.3f} D)")
    print(f"  μ = [{d_film['mu_x']:+.4f}, {d_film['mu_y']:+.4f}, {d_film['mu_z']:+.4f}] e·Å")

    print("\n" + "-" * 72)
    print("Best Interaction (Rank 1):")
    print(f"  {best['substrate_atom']}  –  {best['film_atom']}")
    print(f"  Energy   = {best['energy_eV']:.6f} eV")
    print(f"  Distance = {best['distance_ang']:.4f} Å")
    print(f"  Type     = {best['interaction_type']}")

    print("\nTop 5 interactions by energy:")
    top5_cols = ["Rank", "Substrate Atom", "Film Atom",
                 "Distance (Å)", "Interaction Energy (eV)", "Interaction Type"]
    print(df.head(5)[top5_cols].to_string(index=False))

    return result


# ===========================================================================
# Entry point
# ===========================================================================

if __name__ == "__main__":
    print("\nRunning unit tests …")
    test_dipole_moments()
    test_interaction_table_structure()
    test_best_interaction_is_attractive()
    test_distance_calculation()
    test_cutoff_filter()
    test_energy_symmetry()
    print("\nAll unit tests passed.\n")

    run_full_demo()
