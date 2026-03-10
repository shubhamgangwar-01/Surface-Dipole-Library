"""
ranking.py
----------
Pair-interaction generator and ranked-table builder for the
surface_dipole_library.

Workflow
~~~~~~~~
1. :func:`generate_all_pairs`  – use itertools.product to enumerate every
   (substrate_atom, film_atom) combination inside the cutoff radius.
2. :func:`rank_interactions`   – sort by interaction energy (most negative
   first) and return a pandas DataFrame with a 1-based ``Rank`` column.

Public API
~~~~~~~~~~
    generate_all_pairs(substrate_atoms, film_atoms,
                       centroid1, centroid2,
                       cutoff)            → list of result dicts
    rank_interactions(interactions)       → pandas DataFrame
    best_interaction(df)                  → dict (top-ranked row info)
"""

from __future__ import annotations

import itertools
from typing import List, Optional, Dict, Any

import numpy as np
import pandas as pd

from .atoms import Atom
from .interaction import atom_pair_interaction


# ---------------------------------------------------------------------------
# Pair generator
# ---------------------------------------------------------------------------


def generate_all_pairs(
    substrate_atoms: List[Atom],
    film_atoms: List[Atom],
    centroid1: np.ndarray,
    centroid2: np.ndarray,
    cutoff: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """
    Enumerate every (substrate_atom, film_atom) pair and compute the
    dipole–dipole interaction energy for each.

    Uses ``itertools.product`` to produce the full Cartesian product of
    the two atom lists.  Pairs whose inter-atomic distance exceeds *cutoff*
    are silently skipped.

    Parameters
    ----------
    substrate_atoms : list of Atom
    film_atoms      : list of Atom
    centroid1       : ndarray (3,)
        Geometric centroid of the substrate surface (Å).
    centroid2       : ndarray (3,)
        Geometric centroid of the film surface (Å).
    cutoff : float or None
        Maximum atom–atom distance (Å) to include.
        If ``None`` all pairs are included regardless of distance.

    Returns
    -------
    list of dict
        Each dict is the result of
        :func:`~surface_dipole_library.interaction.atom_pair_interaction`.
        Skipped pairs (distance > cutoff, or non-physical overlap) are
        excluded.

    Raises
    ------
    ValueError
        If either atom list is empty.
    """
    if not substrate_atoms:
        raise ValueError("substrate_atoms is empty.")
    if not film_atoms:
        raise ValueError("film_atoms is empty.")

    results: List[Dict[str, Any]] = []

    for atom1, atom2 in itertools.product(substrate_atoms, film_atoms):
        r = float(np.linalg.norm(atom2.position - atom1.position))

        # Apply distance cutoff
        if cutoff is not None and r > cutoff:
            continue

        try:
            result = atom_pair_interaction(atom1, atom2, centroid1, centroid2)
            results.append(result)
        except ValueError:
            # Non-physical distance (atoms too close) – skip silently
            continue

    return results


# ---------------------------------------------------------------------------
# DataFrame builder and ranker
# ---------------------------------------------------------------------------


def rank_interactions(interactions: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert a list of interaction result dicts into a ranked pandas DataFrame.

    Rows are sorted from the most negative (strongest attractive) energy to
    the most positive (strongest repulsive) energy.  A 1-based ``Rank``
    column is prepended.

    Parameters
    ----------
    interactions : list of dict
        Output of :func:`generate_all_pairs`.

    Returns
    -------
    pandas DataFrame with columns:

    +-----------------------+----------------------------------------------+
    | Column                | Description                                  |
    +=======================+==============================================+
    | Rank                  | 1 = strongest attractive interaction         |
    +-----------------------+----------------------------------------------+
    | Substrate Atom        | Label of the substrate atom                  |
    +-----------------------+----------------------------------------------+
    | Film Atom             | Label of the film atom                       |
    +-----------------------+----------------------------------------------+
    | Substrate Element     | Element symbol of substrate atom             |
    +-----------------------+----------------------------------------------+
    | Film Element          | Element symbol of film atom                  |
    +-----------------------+----------------------------------------------+
    | Substrate Charge (e)  | Partial charge of substrate atom             |
    +-----------------------+----------------------------------------------+
    | Film Charge (e)       | Partial charge of film atom                  |
    +-----------------------+----------------------------------------------+
    | Distance (Å)          | Atom–atom separation                         |
    +-----------------------+----------------------------------------------+
    | mu1 Magnitude (e·Å)   | |mu_substrate| local dipole magnitude        |
    +-----------------------+----------------------------------------------+
    | mu2 Magnitude (e·Å)   | |mu_film| local dipole magnitude             |
    +-----------------------+----------------------------------------------+
    | Interaction Energy (eV) | Dipole–dipole energy (negative = attractive) |
    +-----------------------+----------------------------------------------+
    | Interaction Type      | "attractive" or "repulsive"                  |
    +-----------------------+----------------------------------------------+

    Raises
    ------
    ValueError
        If *interactions* is empty.
    """
    if not interactions:
        raise ValueError(
            "No interactions to rank.  Check your cutoff distance or atom lists."
        )

    rows = []
    for rec in interactions:
        rows.append(
            {
                "Substrate Atom":          rec["atom1"].label,
                "Film Atom":               rec["atom2"].label,
                "Substrate Element":       rec["atom1"].element,
                "Film Element":            rec["atom2"].element,
                "Substrate Charge (e)":    rec["substrate_charge"],
                "Film Charge (e)":         rec["film_charge"],
                "Distance (Å)":            rec["distance"],
                "mu1 Magnitude (e·Å)":     rec["mu1_magnitude"],
                "mu2 Magnitude (e·Å)":     rec["mu2_magnitude"],
                "Interaction Energy (eV)": rec["interaction_energy"],
                "Interaction Type":        rec["interaction_type"],
            }
        )

    df = pd.DataFrame(rows)

    # Sort: most negative energy first (strongest attraction → weakest)
    df = df.sort_values("Interaction Energy (eV)", ascending=True).reset_index(drop=True)

    # Insert 1-based rank column at the front
    df.insert(0, "Rank", range(1, len(df) + 1))

    return df


# ---------------------------------------------------------------------------
# Convenience summary
# ---------------------------------------------------------------------------


def best_interaction(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Return a summary dict for the highest-ranked (most attractive) interaction.

    Parameters
    ----------
    df : pandas DataFrame
        Output of :func:`rank_interactions`.

    Returns
    -------
    dict with keys:
        substrate_atom, film_atom, energy_eV, distance_ang,
        interaction_type, substrate_charge, film_charge
    """
    if df.empty:
        raise ValueError("The interaction table is empty.")

    top = df.iloc[0]
    return {
        "substrate_atom":   top["Substrate Atom"],
        "film_atom":        top["Film Atom"],
        "energy_eV":        top["Interaction Energy (eV)"],
        "distance_ang":     top["Distance (Å)"],
        "interaction_type": top["Interaction Type"],
        "substrate_charge": top["Substrate Charge (e)"],
        "film_charge":      top["Film Charge (e)"],
    }


def print_summary(df: pd.DataFrame, substrate_dipole: dict, film_dipole: dict) -> None:
    """
    Print a human-readable summary to stdout.

    Parameters
    ----------
    df : pandas DataFrame
        Ranked interaction table from :func:`rank_interactions`.
    substrate_dipole : dict
        Output of :func:`~surface_dipole_library.dipole.calculate_dipole`
        for the substrate.
    film_dipole : dict
        Output of :func:`~surface_dipole_library.dipole.calculate_dipole`
        for the film.
    """
    sep = "=" * 72

    print(sep)
    print("  SURFACE DIPOLE INTERACTION ANALYSIS")
    print(sep)

    print("\nSubstrate Dipole Moment:")
    print(f"  μx = {substrate_dipole['mu_x']:+.6f} e·Å")
    print(f"  μy = {substrate_dipole['mu_y']:+.6f} e·Å")
    print(f"  μz = {substrate_dipole['mu_z']:+.6f} e·Å")
    print(f"  |μ| = {substrate_dipole['dipole_magnitude']:.6f} e·Å"
          f"  ({substrate_dipole['dipole_debye']:.4f} D)")

    print("\nFilm Dipole Moment:")
    print(f"  μx = {film_dipole['mu_x']:+.6f} e·Å")
    print(f"  μy = {film_dipole['mu_y']:+.6f} e·Å")
    print(f"  μz = {film_dipole['mu_z']:+.6f} e·Å")
    print(f"  |μ| = {film_dipole['dipole_magnitude']:.6f} e·Å"
          f"  ({film_dipole['dipole_debye']:.4f} D)")

    print(f"\nRanked Interaction Table  ({len(df)} pairs):")
    print(sep)

    # Pretty-print selected columns
    display_cols = [
        "Rank", "Substrate Atom", "Film Atom",
        "Distance (Å)", "Interaction Energy (eV)", "Interaction Type",
    ]
    print(df[display_cols].to_string(index=False, float_format="{:.4f}".format))

    print(sep)
    best = best_interaction(df)
    print("\nBest Interaction (strongest attraction):")
    print(f"  {best['substrate_atom']}  –  {best['film_atom']}")
    print(f"  Energy   = {best['energy_eV']:.6f} eV")
    print(f"  Distance = {best['distance_ang']:.4f} Å")
    print(f"  Type     = {best['interaction_type']}")
    print(sep)
