"""
tests/test_glass_ito.py
-----------------------
Test: Borosilicate glass surface  vs.  Indium Tin Oxide (ITO) thin-film.

This test uses the glass-fixed API introduced in v1.0.0:
    analyze_film_on_glass(film_atoms)
The glass substrate (borosilicate, 12 atoms, ClayFF charges) is loaded
automatically — the user only supplies the ITO film.

Run directly:
    python tests/test_glass_ito.py

or via pytest:
    pytest tests/test_glass_ito.py -v

Scientific context
~~~~~~~~~~~~~~~~~~
ITO — Indium Tin Oxide — is a transparent conductive oxide (TCO) used as the
front electrode in solar cells, flat-panel displays, and touch screens.
It is formed by doping In₂O₃ with ~10 mol% SnO₂.  Sn⁴⁺ substitutes In³⁺
in the bixbyite lattice, donating one free electron per Sn atom, giving ITO
its conductivity while remaining optically transparent.

ITO film surface (In₂O₃ bixbyite, (001) termination):
    In atoms at the surface are 5-fold coordinated (one O ligand missing vs.
    bulk 6-fold).  Sn dopant sits in the same In lattice site.
    Surface bridging O connects two In atoms (O_br, charge ≈ −0.390 e).
    Terminal O is singly bonded to one In (O_term, most negative, ≈ −0.520 e).

Partial charges (Hamad, Moreira & Catlow, J. Phys. Chem. C 2011 / Lewis-Catlow):
    In (5c surface)  : +0.780 e
    Sn (dopant, 4c)  : +0.950 e
    O (bridging)     : −0.390 e
    O (terminal)     : −0.520 e

Expected outcome:
    In/Sn (positive) – O_NBO (negative) pairs dominate attraction.
    Terminal O (most negative film atom) – Si/B (positive) repulsion weak.
    Net interaction: strongly attractive.  ITO is a good candidate for
    glass deposition because its high-valence cations align with the
    negative O_NBO sites on the glass surface.
"""

import sys
import os

# Allow running from the repo root without installing the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pandas as pd

from surface_dipole_library import (
    analyze_film_on_glass,        # NEW glass-fixed API
    analyze_surface_interactions, # kept for cutoff-filter test
    calculate_dipole,
    dipole_summary,
    distance,
    Atom,
    load_from_dict_list,
    BOROSILICATE_GLASS_SURFACE,
)


# ===========================================================================
# ITO film surface definition
# ===========================================================================
#
# Representative (001) surface patch of cubic In₂O₃ with Sn dopant.
# Coordinates in Å.  Film z-range: 3.50 – 5.10 Å (glass ends at 2.35 Å).
# Lateral cell matched to the borosilicate glass unit cell (≈ 5.06 × 4.38 Å).
#
# Atom inventory (11 atoms):
#   3 × In  (surface 5-fold coordinated)
#   1 × Sn  (Sn⁴⁺ dopant substituting one In site)
#   4 × O   (bridging, O_br — connecting two In atoms)
#   3 × O   (terminal, O_term — singly bonded, most negative)
# ---------------------------------------------------------------------------

ITO_FILM = [
    # ── Surface Indium atoms (5-fold coordinated, InO₅) ────────────────────
    # In–In distance ≈ 3.58 Å along [100] in bixbyite In₂O₃ (a = 10.12 Å,
    # surface unit cell ≈ a/√2 ≈ 3.58 Å tiled to match glass cell).
    # Charge +0.780 e — Hamad/Catlow In₂O₃ force field.
    {"element": "In",  "charge":  0.780,  "position": [0.00,  0.00,  3.50], "label": "In5c1_film"},
    {"element": "In",  "charge":  0.780,  "position": [3.58,  0.00,  3.50], "label": "In5c2_film"},
    {"element": "In",  "charge":  0.780,  "position": [1.79,  3.10,  3.50], "label": "In5c3_film"},

    # ── Sn dopant (substitutes one In, 4-fold coordinated at surface) ───────
    # Sn⁴⁺ in an In³⁺ lattice site — slightly more positive charge.
    # Charge +0.950 e — consistent with Sn4+ effective charge in ITO.
    {"element": "Sn",  "charge":  0.950,  "position": [1.79,  1.03,  3.50], "label": "Sn_dp1_film"},

    # ── Bridging oxygens (2-fold coordinated, connecting In–In) ────────────
    # Sit 0.80 Å above the In plane.  Charge −0.390 e (less negative than
    # terminal O because charge is shared between two In atoms).
    {"element": "O",   "charge": -0.390,  "position": [1.79,  0.00,  4.30], "label": "O_br1_film"},
    {"element": "O",   "charge": -0.390,  "position": [0.90,  1.55,  4.30], "label": "O_br2_film"},
    {"element": "O",   "charge": -0.390,  "position": [2.69,  1.55,  4.30], "label": "O_br3_film"},
    {"element": "O",   "charge": -0.390,  "position": [4.48,  1.55,  4.30], "label": "O_br4_film"},

    # ── Terminal oxygens (singly bonded to surface In, dangling bond) ───────
    # Sit 1.40 Å above the In plane.  Most negative atom on the ITO surface
    # (no second In to share the charge).  Charge −0.520 e.
    {"element": "O",   "charge": -0.520,  "position": [0.00,  0.00,  4.90], "label": "O_term1_film"},
    {"element": "O",   "charge": -0.520,  "position": [3.58,  0.00,  4.90], "label": "O_term2_film"},
    {"element": "O",   "charge": -0.520,  "position": [1.79,  3.10,  4.90], "label": "O_term3_film"},
]


# ===========================================================================
# Unit tests (pytest-compatible)
# ===========================================================================


def test_dipole_moments():
    """Dipole vectors are finite and magnitudes are non-negative."""
    glass_atoms = load_from_dict_list(BOROSILICATE_GLASS_SURFACE)
    film_atoms  = load_from_dict_list(ITO_FILM)

    d_glass = calculate_dipole(glass_atoms)
    d_film  = calculate_dipole(film_atoms)

    assert np.isfinite(d_glass["dipole_magnitude"]), "Glass dipole is NaN/Inf"
    assert np.isfinite(d_film["dipole_magnitude"]),  "ITO film dipole is NaN/Inf"
    assert d_glass["dipole_magnitude"] >= 0
    assert d_film["dipole_magnitude"]  >= 0

    print("\n[PASS] test_dipole_moments")
    print(dipole_summary(glass_atoms, "Borosilicate glass surface"))
    print(dipole_summary(film_atoms,  "ITO film surface"))


def test_interaction_table_structure():
    """Interaction table has correct columns, no NaN values, and is sorted."""
    result = analyze_film_on_glass(ITO_FILM, cutoff=8.0, verbose=False)
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

    # Verify ascending energy sort (rank 1 = most negative = strongest attraction)
    energies = df["Interaction Energy (eV)"].tolist()
    assert energies == sorted(energies), "Table is not sorted by energy"

    # Ranks must be 1-based and contiguous
    assert list(df["Rank"]) == list(range(1, len(df) + 1))

    print(f"\n[PASS] test_interaction_table_structure  ({len(df)} pairs)")


def test_best_interaction_is_attractive():
    """Rank-1 interaction must be attractive (In/Sn positive — O_NBO negative).
    ITO cations are strongly positive (+0.78 / +0.95 e); glass NBO is −0.29 e."""
    result = analyze_film_on_glass(ITO_FILM, cutoff=8.0, verbose=False)
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


def test_glass_variant_key_present():
    """Result dict must include 'glass_variant' and 'glass_atoms' keys."""
    result = analyze_film_on_glass(ITO_FILM, cutoff=8.0, verbose=False)

    assert "glass_variant" in result, "Missing key: glass_variant"
    assert "glass_atoms"   in result, "Missing key: glass_atoms"
    assert result["glass_variant"] == "borosilicate"
    assert len(result["glass_atoms"]) == 12   # borosilicate has 12 atoms

    print(f"\n[PASS] test_glass_variant_key_present")
    print(f"  glass_variant = '{result['glass_variant']}'")
    print(f"  glass_atoms   = {len(result['glass_atoms'])} atoms")


def test_distance_calculation():
    """Spot-check distance between an NBO glass atom and a surface In atom."""
    sub  = Atom("O",  charge=-0.290, position=[0.0, 0.0, 1.60])
    film = Atom("In", charge= 0.780, position=[0.0, 0.0, 3.50])
    d = distance(sub, film)
    expected = 1.90  # 3.50 − 1.60 = 1.90 Å (purely z-separated)
    assert abs(d - expected) < 1e-6, f"Distance mismatch: {d:.6f} vs {expected:.6f}"
    print(f"\n[PASS] test_distance_calculation  (d={d:.4f} Å)")


def test_cutoff_filter():
    """With a small cutoff, fewer pairs should survive than with no cutoff."""
    result_all = analyze_film_on_glass(ITO_FILM, cutoff=None, verbose=False)
    result_cut = analyze_film_on_glass(ITO_FILM, cutoff=4.5,  verbose=False)
    assert result_cut["n_pairs"] <= result_all["n_pairs"], (
        "Cutoff did not reduce the number of pairs"
    )
    print(f"\n[PASS] test_cutoff_filter  "
          f"(all={result_all['n_pairs']} pairs, "
          f"cutoff=4.5 Å → {result_cut['n_pairs']} pairs)")


def test_sn_has_attractive_interactions():
    """Sn (+0.950 e) must produce at least one attractive pair with the
    negative glass atoms (O_NBO, O_BO).  Sn is the highest-charge cation
    in ITO, so opposite-sign glass atoms must attract it."""
    result = analyze_film_on_glass(ITO_FILM, cutoff=8.0, verbose=False)
    df = result["interaction_table"]

    sn_attract = df[
        (df["Film Atom"].str.startswith("Sn")) &
        (df["Interaction Type"] == "attractive")
    ]
    assert len(sn_attract) > 0, (
        "Sn atom produced no attractive interactions — "
        "check that Sn is within cutoff of at least one negative glass atom."
    )
    best_sn_energy = sn_attract["Interaction Energy (eV)"].min()
    assert best_sn_energy < 0, f"Best Sn energy not negative: {best_sn_energy:.6f} eV"

    print(f"\n[PASS] test_sn_has_attractive_interactions")
    print(f"  Sn attractive pairs : {len(sn_attract)}")
    print(f"  Best Sn pair energy : {best_sn_energy:.6f} eV")


def test_energy_symmetry():
    """Swapping μ₁ ↔ μ₂ must not change the dipole–dipole energy."""
    from surface_dipole_library import dipole_dipole_energy
    rng = np.random.default_rng(0)
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
    Execute the complete glass-fixed analysis for ITO and print results.
    Demonstrates the new analyze_film_on_glass() API.
    """
    print("\n" + "=" * 72)
    print("  DEMO: Borosilicate Glass  vs.  ITO (Indium Tin Oxide) Thin Film")
    print("  Using glass-fixed API: analyze_film_on_glass(film_atoms)")
    print("=" * 72)

    result = analyze_film_on_glass(
        film_atoms=ITO_FILM,
        cutoff=8.0,
        glass_variant="borosilicate",
        verbose=True,
    )

    df   = result["interaction_table"]
    best = result["best_interaction"]

    pd.set_option("display.max_rows",    200)
    pd.set_option("display.max_columns", 20)
    pd.set_option("display.width",       130)
    pd.set_option("display.float_format", "{:.4f}".format)

    print("\nFull Ranked Interaction Table:")
    print(df.to_string(index=False))

    print("\n" + "-" * 72)
    print(f"Glass variant used : {result['glass_variant']}")
    print(f"Glass atoms        : {len(result['glass_atoms'])}")
    print(f"Film atoms         : {len(result['film_atoms'])}")
    print(f"Total pairs        : {result['n_pairs']}")

    print("\n" + "-" * 72)
    print("Glass Substrate Dipole:")
    d_sub = result["substrate_dipole"]
    print(f"  |μ| = {d_sub['dipole_magnitude']:.4f} e·Å  "
          f"({d_sub['dipole_debye']:.3f} D)")
    print(f"  μ   = [{d_sub['mu_x']:+.4f}, {d_sub['mu_y']:+.4f}, {d_sub['mu_z']:+.4f}] e·Å")

    print("\nITO Film Dipole:")
    d_film = result["film_dipole"]
    print(f"  |μ| = {d_film['dipole_magnitude']:.4f} e·Å  "
          f"({d_film['dipole_debye']:.3f} D)")
    print(f"  μ   = [{d_film['mu_x']:+.4f}, {d_film['mu_y']:+.4f}, {d_film['mu_z']:+.4f}] e·Å")

    print("\n" + "-" * 72)
    print("Best Interaction (Rank 1):")
    print(f"  {best['substrate_atom']}  –  {best['film_atom']}")
    print(f"  Energy   = {best['energy_eV']:.6f} eV")
    print(f"  Distance = {best['distance_ang']:.4f} Å")
    print(f"  Type     = {best['interaction_type']}")
    print(f"  Glass atom charge : {best['substrate_charge']:+.3f} e")
    print(f"  Film atom charge  : {best['film_charge']:+.3f} e")

    print("\nTop 5 interactions:")
    top5_cols = ["Rank", "Substrate Atom", "Film Atom",
                 "Substrate Charge (e)", "Film Charge (e)",
                 "Distance (Å)", "Interaction Energy (eV)", "Interaction Type"]
    print(df.head(5)[top5_cols].to_string(index=False))

    print("\nBottom 5 interactions (most repulsive):")
    print(df.tail(5)[top5_cols].to_string(index=False))

    # ── Summary by film atom type ─────────────────────────────────────────
    print("\n" + "-" * 72)
    print("Energy summary by film atom element:")
    df["film_element"] = df["Film Atom"].str.extract(r"^([A-Za-z]+)")
    summary = (
        df.groupby("film_element")["Interaction Energy (eV)"]
        .agg(["min", "mean", "max", "count"])
        .rename(columns={"min": "Best (eV)", "mean": "Avg (eV)",
                         "max": "Worst (eV)", "count": "Pairs"})
        .sort_values("Best (eV)")
    )
    print(summary.to_string(float_format="{:.4f}".format))

    # ── Attraction vs repulsion count ─────────────────────────────────────
    attract = (df["Interaction Type"] == "attractive").sum()
    repulse = (df["Interaction Type"] == "repulsive").sum()
    neutral = (df["Interaction Type"] == "neutral").sum()
    print(f"\nPair statistics:")
    print(f"  Attractive : {attract}")
    print(f"  Repulsive  : {repulse}")
    print(f"  Neutral    : {neutral}")

    return result


# ===========================================================================
# Entry point
# ===========================================================================


if __name__ == "__main__":
    print("\nRunning unit tests …")
    test_dipole_moments()
    test_interaction_table_structure()
    test_best_interaction_is_attractive()
    test_glass_variant_key_present()
    test_distance_calculation()
    test_cutoff_filter()
    test_sn_has_attractive_interactions()
    test_energy_symmetry()
    print("\n" + "=" * 72)
    print("All 8 unit tests passed.")
    print("=" * 72)

    run_full_demo()
