"""
dipole.py
---------
Dipole moment calculations for the surface_dipole_library.

Physical background
~~~~~~~~~~~~~~~~~~~
The electric dipole moment of a collection of point charges is

    μ = Σᵢ qᵢ rᵢ

where qᵢ is the partial charge (in units of *e*) and rᵢ is the 3-D
position vector (in Å).  The result μ is therefore in units of **e·Å**.

Unit conversion notes
~~~~~~~~~~~~~~~~~~~~~
    1 e·Å  =  1.602 176 634 × 10⁻²⁹ C·m
           ≈  4.803 204 Debye

    1 Debye = 3.335 640 95 × 10⁻³⁰ C·m

Public API
~~~~~~~~~~
    calculate_dipole(atoms)           → dict with μ vector, |μ|, components
    calculate_centroid(atoms)         → geometric centroid (numpy ndarray)
    atomic_local_dipole(atom, centre) → effective local dipole vector for one atom
"""

from __future__ import annotations

from typing import Dict, Any, List

import numpy as np

from .atoms import Atom


# ---------------------------------------------------------------------------
# Unit conversion constants
# ---------------------------------------------------------------------------

DEBYE_PER_E_ANG: float = 4.803_204_298  # 1 e·Å expressed in Debye
E_ANG_TO_CM: float = 1.602_176_634e-29  # 1 e·Å in C·m


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------


def calculate_dipole(atoms: List[Atom]) -> Dict[str, Any]:
    """
    Calculate the electric dipole moment of a group of atoms.

    The formula implemented is

        **μ** = Σᵢ qᵢ **rᵢ**

    where *qᵢ* is the partial charge (e) and **rᵢ** is the position (Å).

    Parameters
    ----------
    atoms : list of Atom
        Atoms belonging to the surface group whose dipole is required.
        At least one atom must be supplied.

    Returns
    -------
    dict with keys:

    ``dipole_vector``
        numpy ndarray, shape (3,), in **e·Å**.
    ``dipole_magnitude``
        float, |**μ**| in **e·Å**.
    ``mu_x``, ``mu_y``, ``mu_z``
        Cartesian components in **e·Å**.
    ``dipole_debye``
        |**μ**| in **Debye** (1 e·Å ≈ 4.803 D).
    ``total_charge``
        Net charge of the group (Σqᵢ).
    ``n_atoms``
        Number of atoms in the group.

    Raises
    ------
    ValueError
        If *atoms* is empty.

    Examples
    --------
    >>> from surface_dipole_library.atoms import Atom
    >>> from surface_dipole_library.dipole import calculate_dipole
    >>> atoms = [
    ...     Atom("Si", charge=0.3, position=[0.0, 0.0, 0.0]),
    ...     Atom("O",  charge=-0.2, position=[1.0, 0.0, 0.0]),
    ...     Atom("O",  charge=-0.1, position=[0.0, 1.0, 0.0]),
    ... ]
    >>> d = calculate_dipole(atoms)
    >>> d["dipole_vector"]
    array([-0.2,  0.1,  0. ])   # e·Å  (approximately)
    """
    if not atoms:
        raise ValueError("The atom list is empty; cannot compute a dipole moment.")

    mu = np.zeros(3, dtype=float)
    total_q = 0.0

    for atom in atoms:
        mu += atom.charge * atom.position
        total_q += atom.charge

    magnitude = float(np.linalg.norm(mu))

    return {
        "dipole_vector": mu,
        "dipole_magnitude": magnitude,
        "mu_x": float(mu[0]),
        "mu_y": float(mu[1]),
        "mu_z": float(mu[2]),
        "dipole_debye": magnitude * DEBYE_PER_E_ANG,
        "total_charge": float(total_q),
        "n_atoms": len(atoms),
    }


def calculate_centroid(atoms: List[Atom]) -> np.ndarray:
    """
    Return the geometric centroid (unweighted mean position) of the atoms.

    Parameters
    ----------
    atoms : list of Atom

    Returns
    -------
    numpy ndarray, shape (3,), in Å.

    Raises
    ------
    ValueError
        If *atoms* is empty.
    """
    if not atoms:
        raise ValueError("The atom list is empty; cannot compute a centroid.")
    positions = np.array([a.position for a in atoms], dtype=float)
    return positions.mean(axis=0)


def charge_centroid(atoms: List[Atom]) -> np.ndarray:
    """
    Return the charge-weighted centroid (centre of charge) of the atoms.

    For a set of partial charges this is analogous to the centre of mass.

    Parameters
    ----------
    atoms : list of Atom

    Returns
    -------
    numpy ndarray, shape (3,), in Å.

    Notes
    -----
    If the net charge is zero the result defaults to the geometric centroid
    to avoid division by zero.
    """
    if not atoms:
        raise ValueError("The atom list is empty.")

    total_q = sum(abs(a.charge) for a in atoms)
    if total_q < 1e-12:
        return calculate_centroid(atoms)

    weighted = np.zeros(3, dtype=float)
    for atom in atoms:
        weighted += abs(atom.charge) * atom.position
    return weighted / total_q


def atomic_local_dipole(atom: Atom, centroid: np.ndarray) -> np.ndarray:
    """
    Effective local dipole moment of a single atom relative to a reference
    centroid.

    The local dipole is defined as

        **μ**ᵢ = qᵢ (**rᵢ** − **r**_centroid)

    This decomposes the total group dipole into per-atom contributions:

        Σᵢ **μ**ᵢ = Σᵢ qᵢ (**rᵢ** − **r**_c) = **μ**_group − Q_tot **r**_c

    (where Q_tot = Σqᵢ).  When the group is neutral, Σᵢ **μ**ᵢ = **μ**_group
    exactly.

    Parameters
    ----------
    atom : Atom
    centroid : numpy ndarray, shape (3,)
        Reference point (geometric or charge centroid of the group), in Å.

    Returns
    -------
    numpy ndarray, shape (3,), in **e·Å**.
    """
    return atom.charge * (atom.position - centroid)


def dipole_summary(atoms: List[Atom], group_name: str = "group") -> str:
    """
    Return a human-readable summary string of the dipole moment.

    Parameters
    ----------
    atoms : list of Atom
    group_name : str
        Label printed in the header line.

    Returns
    -------
    str
    """
    d = calculate_dipole(atoms)
    lines = [
        f"Dipole moment of {group_name}:",
        f"  μx = {d['mu_x']:+.6f} e·Å",
        f"  μy = {d['mu_y']:+.6f} e·Å",
        f"  μz = {d['mu_z']:+.6f} e·Å",
        f"  |μ| = {d['dipole_magnitude']:.6f} e·Å  ({d['dipole_debye']:.4f} D)",
        f"  Net charge Q = {d['total_charge']:+.4f} e",
        f"  Atoms: {d['n_atoms']}",
    ]
    return "\n".join(lines)
