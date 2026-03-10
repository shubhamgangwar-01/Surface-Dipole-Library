"""
main.py
-------
High-level user-facing API for the surface_dipole_library.

Primary entry point
~~~~~~~~~~~~~~~~~~~
    from surface_dipole_library import analyze_surface_interactions

    result = analyze_surface_interactions(
        substrate_atoms,   # list[dict] or list[Atom]
        film_atoms,        # list[dict] or list[Atom]
        cutoff=6.0,        # Å – maximum pair distance to consider
        verbose=True,      # print summary table to stdout
    )

    print(result["interaction_table"])

Return value
~~~~~~~~~~~~
The function returns a dict with keys:

    substrate_atoms   – list of Atom
    film_atoms        – list of Atom
    substrate_dipole  – dict  (vector, magnitude, components, Debye)
    film_dipole       – dict  (vector, magnitude, components, Debye)
    interaction_table – pandas DataFrame (ranked, best first)
    best_interaction  – dict  (top-ranked pair summary)
    n_pairs           – int   (number of pairs evaluated)
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Union, Any

import numpy as np
import pandas as pd

from .atoms import Atom, atoms_from_dicts
from .dipole import calculate_dipole, calculate_centroid
from .ranking import generate_all_pairs, rank_interactions, best_interaction, print_summary
from .io import (
    load_from_dict_list,
    load_from_xyz,
    load_from_ase,
    load_from_poscar,
    load_from_cif,
)


# ---------------------------------------------------------------------------
# Type alias
# ---------------------------------------------------------------------------

AtomInput = Union[List[Dict], List[Atom]]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _coerce_atoms(raw: AtomInput, prefix: str = "") -> List[Atom]:
    """
    Accept either a list-of-dicts or a list-of-Atom objects and always
    return a list of :class:`Atom` objects with unique labels.
    """
    if not raw:
        raise ValueError("Atom list must not be empty.")

    # Already Atom objects – copy to avoid mutating caller's data
    if isinstance(raw[0], Atom):
        from copy import deepcopy
        atoms = [deepcopy(a) for a in raw]
    else:
        atoms = load_from_dict_list(raw, prefix=prefix)  # type: ignore[arg-type]

    return atoms


# ---------------------------------------------------------------------------
# Main API
# ---------------------------------------------------------------------------


def analyze_surface_interactions(
    substrate_atoms: AtomInput,
    film_atoms: AtomInput,
    cutoff: Optional[float] = None,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Compute dipole moments and ranked dipole–dipole interactions between
    two surface atom groups.

    Parameters
    ----------
    substrate_atoms : list of dict or list of Atom
        Surface atoms of the substrate (e.g. SiO₂ glass surface).
        Each dict must contain ``"element"``, ``"charge"``, ``"position"``.
    film_atoms : list of dict or list of Atom
        Surface atoms of the thin film (e.g. TiO₂ film).
    cutoff : float or None
        Maximum atom–atom distance (Å) to include in the interaction
        table.  Set to ``None`` to include all pairs regardless of
        distance (may be slow for large supercells).
        Default: ``None``.
    verbose : bool
        If ``True`` (default), print a formatted summary table to stdout.

    Returns
    -------
    dict with keys:

    ``substrate_atoms``
        list of :class:`~surface_dipole_library.atoms.Atom` (labelled).
    ``film_atoms``
        list of :class:`~surface_dipole_library.atoms.Atom` (labelled).
    ``substrate_dipole``
        dict – dipole vector (e·Å), magnitude, Cartesian components,
        value in Debye, net charge, atom count.
    ``film_dipole``
        dict – same structure as ``substrate_dipole``.
    ``interaction_table``
        pandas DataFrame – ranked from strongest attraction (most negative
        energy) to strongest repulsion (most positive energy).
        See :func:`~surface_dipole_library.ranking.rank_interactions`
        for the full column list.
    ``best_interaction``
        dict – summary of the top-ranked pair:
        substrate_atom, film_atom, energy_eV, distance_ang,
        interaction_type, substrate_charge, film_charge.
    ``n_pairs``
        int – total number of atom pairs evaluated.

    Raises
    ------
    ValueError
        If either atom list is empty, or if no pairs fall within *cutoff*.

    Examples
    --------
    >>> from surface_dipole_library import analyze_surface_interactions
    >>>
    >>> substrate = [
    ...     {"element": "Si", "charge":  0.30,  "position": [0.0, 0.0, 0.0]},
    ...     {"element": "O",  "charge": -0.15,  "position": [1.6, 0.0, 0.0]},
    ...     {"element": "O",  "charge": -0.15,  "position": [0.0, 1.6, 0.0]},
    ... ]
    >>> film = [
    ...     {"element": "Ti", "charge":  0.50,  "position": [0.0, 0.0, 3.0]},
    ...     {"element": "O",  "charge": -0.25,  "position": [1.6, 0.0, 3.0]},
    ... ]
    >>> result = analyze_surface_interactions(substrate, film, cutoff=6.0)
    >>> print(result["interaction_table"])
    """
    # ------------------------------------------------------------------
    # 1. Prepare atom lists
    # ------------------------------------------------------------------
    sub_atoms  = _coerce_atoms(substrate_atoms, prefix="sub_")
    film_atoms_ = _coerce_atoms(film_atoms,      prefix="film_")

    # ------------------------------------------------------------------
    # 2. Dipole moments of each surface group
    # ------------------------------------------------------------------
    sub_dipole  = calculate_dipole(sub_atoms)
    film_dipole = calculate_dipole(film_atoms_)

    # ------------------------------------------------------------------
    # 3. Geometric centroids (reference for local atomic dipoles)
    # ------------------------------------------------------------------
    centroid1 = calculate_centroid(sub_atoms)
    centroid2 = calculate_centroid(film_atoms_)

    # ------------------------------------------------------------------
    # 4. Enumerate all pairs and compute interactions
    # ------------------------------------------------------------------
    interactions = generate_all_pairs(
        sub_atoms, film_atoms_,
        centroid1, centroid2,
        cutoff=cutoff,
    )

    if not interactions:
        raise ValueError(
            f"No atom pairs found within cutoff={cutoff} Å.  "
            "Increase the cutoff or check that the substrate and film "
            "atom positions are in the same Cartesian coordinate system."
        )

    # ------------------------------------------------------------------
    # 5. Rank interactions
    # ------------------------------------------------------------------
    table = rank_interactions(interactions)
    best  = best_interaction(table)

    # ------------------------------------------------------------------
    # 6. Optional verbose output
    # ------------------------------------------------------------------
    if verbose:
        print_summary(table, sub_dipole, film_dipole)

    return {
        "substrate_atoms":    sub_atoms,
        "film_atoms":         film_atoms_,
        "substrate_dipole":   sub_dipole,
        "film_dipole":        film_dipole,
        "interaction_table":  table,
        "best_interaction":   best,
        "n_pairs":            len(interactions),
    }


# ---------------------------------------------------------------------------
# File-based entry points
# ---------------------------------------------------------------------------


def analyze_from_xyz(
    substrate_file: Union[str, Path],
    film_file: Union[str, Path],
    cutoff: Optional[float] = None,
    has_charges: bool = True,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Load both surfaces from custom XYZ files and run the full analysis.

    Parameters
    ----------
    substrate_file : str or Path
        Path to the substrate XYZ file (5-column format with charges).
    film_file : str or Path
        Path to the film XYZ file.
    cutoff : float or None
        Distance cutoff in Å.
    has_charges : bool
        If ``True`` (default) expect the 5th column to be the partial charge.
    verbose : bool

    Returns
    -------
    Same dict as :func:`analyze_surface_interactions`.
    """
    sub_atoms  = load_from_xyz(substrate_file, prefix="sub_", has_charges=has_charges)
    film_atoms = load_from_xyz(film_file,      prefix="film_", has_charges=has_charges)

    return analyze_surface_interactions(sub_atoms, film_atoms,
                                        cutoff=cutoff, verbose=verbose)


def analyze_from_ase(
    substrate_file: Union[str, Path],
    film_file: Union[str, Path],
    substrate_charges: Optional[Dict[str, float]] = None,
    film_charges: Optional[Dict[str, float]] = None,
    cutoff: Optional[float] = None,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Load both surfaces via ASE (supports .cif, POSCAR, .xyz, etc.)
    and run the full analysis.

    Parameters
    ----------
    substrate_file : str or Path
    film_file : str or Path
    substrate_charges : dict {element: charge} or None
    film_charges : dict {element: charge} or None
    cutoff : float or None
    verbose : bool

    Returns
    -------
    Same dict as :func:`analyze_surface_interactions`.
    """
    sub_atoms  = load_from_ase(substrate_file, charges=substrate_charges, prefix="sub_")
    film_atoms = load_from_ase(film_file,      charges=film_charges,      prefix="film_")

    return analyze_surface_interactions(sub_atoms, film_atoms,
                                        cutoff=cutoff, verbose=verbose)
