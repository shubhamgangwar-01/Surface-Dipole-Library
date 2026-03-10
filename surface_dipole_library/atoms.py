"""
atoms.py
--------
Atom dataclass for the surface_dipole_library.

Each Atom stores:
  - element  : chemical symbol (str)
  - charge   : partial charge in units of elementary charge e (float)
  - position : 3D Cartesian coordinate vector in Angstroms (numpy ndarray)
  - label    : unique human-readable identifier (str, auto-generated if omitted)
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class Atom:
    """
    Represents a single surface atom with a partial charge and 3-D position.

    Parameters
    ----------
    element : str
        Chemical symbol, e.g. ``"Si"``, ``"O"``, ``"Ti"``.
    charge : float
        Partial charge in units of the elementary charge *e*.
        Positive for cations, negative for anions.
    position : array-like, shape (3,)
        Cartesian coordinates (x, y, z) in Angstroms.
    label : str, optional
        Unique label used in output tables.  If not given it defaults to
        the element symbol (duplicate labels are resolved by the helper
        :func:`assign_labels`).

    Examples
    --------
    >>> from surface_dipole_library.atoms import Atom
    >>> si = Atom(element="Si", charge=0.3, position=[0.0, 0.0, 0.0])
    >>> si.position
    array([0., 0., 0.])
    """

    element: str
    charge: float
    position: np.ndarray
    label: Optional[str] = field(default=None)

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def __post_init__(self) -> None:
        self.position = np.asarray(self.position, dtype=float)
        if self.position.shape != (3,):
            raise ValueError(
                f"position must be a 3-element array-like, got shape {self.position.shape}"
            )
        if self.label is None:
            self.label = self.element

    # ------------------------------------------------------------------
    # Alternative constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Atom":
        """
        Build an :class:`Atom` from a plain Python dictionary.

        The dict must contain ``"element"``, ``"charge"``, and
        ``"position"`` keys.  An optional ``"label"`` key is supported.

        Parameters
        ----------
        data : dict
            Example::

                {"element": "Si", "charge": 0.3, "position": [0.0, 0.0, 0.0]}

        Returns
        -------
        Atom
        """
        required = {"element", "charge", "position"}
        missing = required - data.keys()
        if missing:
            raise KeyError(f"Atom dict is missing required keys: {missing}")

        return cls(
            element=str(data["element"]),
            charge=float(data["charge"]),
            position=np.array(data["position"], dtype=float),
            label=data.get("label", None),
        )

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Return a plain-dict representation (JSON-serialisable)."""
        return {
            "element": self.element,
            "charge": self.charge,
            "position": self.position.tolist(),
            "label": self.label,
        }

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        pos = ", ".join(f"{v:.4f}" for v in self.position)
        return (
            f"Atom(label={self.label!r}, element={self.element!r}, "
            f"charge={self.charge:+.4f} e, position=[{pos}] Å)"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Atom):
            return NotImplemented
        return (
            self.element == other.element
            and np.isclose(self.charge, other.charge)
            and np.allclose(self.position, other.position)
            and self.label == other.label
        )


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------


def atoms_from_dicts(data: List[Dict[str, Any]], prefix: str = "") -> List[Atom]:
    """
    Convert a list of atom dictionaries to a list of :class:`Atom` objects,
    assigning unique sequential labels.

    Parameters
    ----------
    data : list of dict
        Each dict follows the format expected by :meth:`Atom.from_dict`.
    prefix : str
        Optional prefix prepended to auto-generated labels, e.g. ``"sub_"``.

    Returns
    -------
    list of Atom
    """
    atoms: List[Atom] = []
    element_counts: Dict[str, int] = {}

    for d in data:
        atom = Atom.from_dict(d)
        # Build a unique label: element + sequential index per element
        count = element_counts.get(atom.element, 0) + 1
        element_counts[atom.element] = count
        if atom.label == atom.element:
            # label was not specified explicitly → auto-generate
            atom.label = f"{prefix}{atom.element}{count}"
        atoms.append(atom)

    return atoms


def assign_labels(atoms: List[Atom], prefix: str = "") -> None:
    """
    Modify the *label* attribute of each atom in-place so that every label
    is unique within the list.

    Atoms whose label already differs from their element symbol are left
    untouched.  All others get a sequential suffix appended.

    Parameters
    ----------
    atoms : list of Atom
        Atoms to label (modified in-place).
    prefix : str
        Prefix prepended to every auto-generated label.
    """
    element_counts: Dict[str, int] = {}
    for atom in atoms:
        if atom.label == atom.element:
            count = element_counts.get(atom.element, 0) + 1
            element_counts[atom.element] = count
            atom.label = f"{prefix}{atom.element}{count}"
