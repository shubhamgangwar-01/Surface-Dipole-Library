"""
geometry.py
-----------
Geometric helper functions for the surface_dipole_library.

All distances and positions are in **Angstroms (Å)**.

Public API
~~~~~~~~~~
    displacement_vector(atom1, atom2)  → ndarray(3,)
    distance(atom1, atom2)             → float (Å)
    unit_vector(v)                     → ndarray(3,)
    angle_between(v1, v2)              → float (degrees)
    midpoint(atom1, atom2)             → ndarray(3,)
    are_within_cutoff(atom1, atom2,
                      cutoff)          → bool
"""

from __future__ import annotations

from typing import List, Tuple

import numpy as np

from .atoms import Atom


# ---------------------------------------------------------------------------
# Core geometry primitives
# ---------------------------------------------------------------------------


def displacement_vector(atom1: Atom, atom2: Atom) -> np.ndarray:
    """
    Return the displacement vector **r** from *atom1* to *atom2*.

    **r** = **r**₂ − **r**₁

    Parameters
    ----------
    atom1, atom2 : Atom

    Returns
    -------
    numpy ndarray, shape (3,), in Å.
    """
    return atom2.position - atom1.position


def distance(atom1: Atom, atom2: Atom) -> float:
    """
    Return the scalar Euclidean distance between two atoms (in Å).

    Parameters
    ----------
    atom1, atom2 : Atom

    Returns
    -------
    float  (Å)

    Examples
    --------
    >>> from surface_dipole_library.atoms import Atom
    >>> from surface_dipole_library.geometry import distance
    >>> a1 = Atom("Si", 0.3, [0.0, 0.0, 0.0])
    >>> a2 = Atom("Ti", 0.5, [0.0, 0.0, 3.0])
    >>> distance(a1, a2)
    3.0
    """
    return float(np.linalg.norm(displacement_vector(atom1, atom2)))


def unit_vector(v: np.ndarray) -> np.ndarray:
    """
    Return the unit vector along *v*.

    Parameters
    ----------
    v : array-like, shape (3,)

    Returns
    -------
    numpy ndarray, shape (3,).

    Raises
    ------
    ValueError
        If *v* is the zero vector.
    """
    v = np.asarray(v, dtype=float)
    norm = np.linalg.norm(v)
    if norm < 1e-14:
        raise ValueError("Cannot normalise the zero vector.")
    return v / norm


def angle_between(v1: np.ndarray, v2: np.ndarray) -> float:
    """
    Return the angle (in degrees) between vectors *v1* and *v2*.

    Parameters
    ----------
    v1, v2 : array-like, shape (3,)

    Returns
    -------
    float (degrees), in the range [0, 180].
    """
    u1 = unit_vector(np.asarray(v1, dtype=float))
    u2 = unit_vector(np.asarray(v2, dtype=float))
    cos_theta = np.clip(np.dot(u1, u2), -1.0, 1.0)
    return float(np.degrees(np.arccos(cos_theta)))


def midpoint(atom1: Atom, atom2: Atom) -> np.ndarray:
    """
    Return the geometric midpoint between two atoms (in Å).

    Parameters
    ----------
    atom1, atom2 : Atom

    Returns
    -------
    numpy ndarray, shape (3,), in Å.
    """
    return 0.5 * (atom1.position + atom2.position)


def are_within_cutoff(atom1: Atom, atom2: Atom, cutoff: float) -> bool:
    """
    Return ``True`` if the distance between two atoms is ≤ *cutoff* Å.

    Parameters
    ----------
    atom1, atom2 : Atom
    cutoff : float
        Distance threshold in Å.

    Returns
    -------
    bool
    """
    return distance(atom1, atom2) <= cutoff


# ---------------------------------------------------------------------------
# Pair-distance utilities
# ---------------------------------------------------------------------------


def pairwise_distances(
    atoms_a: List[Atom],
    atoms_b: List[Atom],
) -> np.ndarray:
    """
    Compute a distance matrix between two atom lists.

    Parameters
    ----------
    atoms_a : list of Atom, length M
    atoms_b : list of Atom, length N

    Returns
    -------
    numpy ndarray, shape (M, N), distances in Å.
    """
    pos_a = np.array([a.position for a in atoms_a], dtype=float)  # (M, 3)
    pos_b = np.array([a.position for a in atoms_b], dtype=float)  # (N, 3)
    # Broadcast: (M, 1, 3) - (1, N, 3) → (M, N, 3)
    diff = pos_a[:, np.newaxis, :] - pos_b[np.newaxis, :, :]
    return np.linalg.norm(diff, axis=-1)  # (M, N)


def nearest_neighbours(
    atoms_a: List[Atom],
    atoms_b: List[Atom],
    n: int = 1,
) -> List[Tuple[Atom, Atom, float]]:
    """
    Find the *n* closest (atom_a, atom_b) pairs by distance.

    Parameters
    ----------
    atoms_a : list of Atom  (e.g. substrate)
    atoms_b : list of Atom  (e.g. film)
    n : int
        Number of nearest neighbour pairs to return.

    Returns
    -------
    list of (Atom_a, Atom_b, distance_float) tuples,
    sorted ascending by distance, length min(n, M×N).
    """
    dist_mat = pairwise_distances(atoms_a, atoms_b)  # (M, N)
    flat_indices = np.argsort(dist_mat, axis=None)[:n]
    rows, cols = np.unravel_index(flat_indices, dist_mat.shape)
    result = []
    for r, c in zip(rows, cols):
        result.append((atoms_a[int(r)], atoms_b[int(c)], float(dist_mat[r, c])))
    return result
