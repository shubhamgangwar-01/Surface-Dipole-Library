"""
io.py
-----
Structure-file readers for the surface_dipole_library.

Supported formats
~~~~~~~~~~~~~~~~~
1.  **Dict list**    – Python list of dicts (primary in-memory format).
2.  **Custom XYZ**   – Plain-text file; 5 columns per atom line:
                       ``Element  x  y  z  charge``
3.  **Standard XYZ** – 4-column XYZ (no charge).  Charges must be
                       supplied via the ``charges`` kwarg.
4.  **ASE-readable** – Any format ASE understands (.cif, POSCAR, .vasp,
                       .xyz, etc.).  Charges are taken from
                       ``Atoms.get_initial_charges()`` or the
                       ``charges`` kwarg.
5.  **Pymatgen Structure** – Loads a pymatgen Structure and assigns
                             oxidation states as charges (optional).

For .cif / POSCAR files ASE (and optionally pymatgen) must be installed:
    pip install ase pymatgen

Public API
~~~~~~~~~~
    load_from_dict_list(data, prefix)
    load_from_xyz(filepath, prefix, has_charges)
    load_from_ase(filepath, charges, prefix)
    load_from_poscar(filepath, charges, prefix)
    load_from_cif(filepath, charges, prefix)
    write_xyz(atoms, filepath)
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional, Union

import numpy as np

from .atoms import Atom, atoms_from_dicts


# ---------------------------------------------------------------------------
# 1. Dict-list (always available)
# ---------------------------------------------------------------------------


def load_from_dict_list(
    data: List[Dict],
    prefix: str = "",
) -> List[Atom]:
    """
    Convert a plain Python list-of-dicts to a list of :class:`Atom` objects.

    Each dict must contain ``"element"``, ``"charge"``, and ``"position"``.
    An optional ``"label"`` key is supported.

    Parameters
    ----------
    data : list of dict
    prefix : str
        Prepended to auto-generated labels (e.g. ``"sub_"`` or ``"film_"``).

    Returns
    -------
    list of Atom

    Examples
    --------
    >>> from surface_dipole_library.io import load_from_dict_list
    >>> raw = [
    ...     {"element": "Si", "charge": 0.3,  "position": [0.0, 0.0, 0.0]},
    ...     {"element": "O",  "charge": -0.15, "position": [1.6, 0.0, 0.0]},
    ... ]
    >>> atoms = load_from_dict_list(raw, prefix="sub_")
    """
    return atoms_from_dicts(data, prefix=prefix)


# ---------------------------------------------------------------------------
# 2. Custom XYZ (5-column, charge included)
# ---------------------------------------------------------------------------

def load_from_xyz(
    filepath: Union[str, Path],
    prefix: str = "",
    has_charges: bool = True,
) -> List[Atom]:
    """
    Load atoms from an XYZ-format file.

    Two sub-formats are supported:

    **5-column (custom, default)**::

        <n_atoms>
        comment line
        Si   0.000   0.000   0.000   0.30
        O    1.600   0.000   0.000  -0.15
        ...

    **4-column (standard XYZ, has_charges=False)**::

        <n_atoms>
        comment line
        Si   0.000   0.000   0.000
        O    1.600   0.000   0.000
        ...

    If ``has_charges=False`` all charges default to ``0.0``; use the
    returned list to set ``atom.charge`` manually or call
    :func:`load_from_ase` which accepts a ``charges`` mapping.

    Parameters
    ----------
    filepath : str or Path
    prefix : str
        Label prefix for auto-generated labels.
    has_charges : bool
        ``True`` (default) expects a 5th column for the partial charge.

    Returns
    -------
    list of Atom

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If a data line has an unexpected number of columns.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"XYZ file not found: {filepath}")

    atoms: List[Atom] = []
    element_counts: Dict[str, int] = {}

    with open(filepath, "r") as fh:
        lines = [ln.strip() for ln in fh if ln.strip()]

    # Skip the atom-count line and comment line
    start = 0
    if lines and lines[0].lstrip("-").isdigit():
        start = 1          # skip count line
    if len(lines) > start and not _is_data_line(lines[start]):
        start += 1         # skip comment line

    for ln in lines[start:]:
        cols = ln.split()
        if has_charges:
            if len(cols) < 5:
                raise ValueError(
                    f"Expected 5 columns (element x y z charge) but got: {ln!r}"
                )
            element, x, y, z, charge = cols[0], float(cols[1]), float(cols[2]), float(cols[3]), float(cols[4])
        else:
            if len(cols) < 4:
                raise ValueError(
                    f"Expected 4 columns (element x y z) but got: {ln!r}"
                )
            element, x, y, z = cols[0], float(cols[1]), float(cols[2]), float(cols[3])
            charge = 0.0

        count = element_counts.get(element, 0) + 1
        element_counts[element] = count
        label = f"{prefix}{element}{count}"
        atoms.append(Atom(element=element, charge=charge,
                          position=np.array([x, y, z]), label=label))

    return atoms


def _is_data_line(line: str) -> bool:
    """Return True if the line looks like an atom data line."""
    parts = line.split()
    if len(parts) < 4:
        return False
    try:
        float(parts[1])
        float(parts[2])
        float(parts[3])
        return True
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# 3. ASE reader (optional dependency)
# ---------------------------------------------------------------------------


def load_from_ase(
    filepath: Union[str, Path],
    charges: Optional[Dict[str, float]] = None,
    prefix: str = "",
    index: int = 0,
) -> List[Atom]:
    """
    Load atoms from any ASE-supported structure file.

    Supported formats include ``.xyz``, ``.cif``, ``POSCAR``/``CONTCAR``,
    ``.vasp``, ``.extxyz``, ``.json``, etc.

    Partial charges are read in this priority order:

    1. ``charges`` dict supplied by the caller (keyed by element symbol).
    2. ``atoms.get_initial_charges()`` if ASE has stored them
       (e.g. from an extended XYZ file with a ``charges`` array).
    3. Zero for every atom if no charge information is found.

    Parameters
    ----------
    filepath : str or Path
    charges : dict {element: charge} or None
        Optional override mapping element symbol → partial charge.
        E.g. ``{"Si": 0.3, "O": -0.15, "Ti": 0.5}``.
    prefix : str
        Label prefix.
    index : int
        Frame index for multi-frame files (default 0 = first frame).

    Returns
    -------
    list of Atom

    Raises
    ------
    ImportError
        If ASE is not installed.
    FileNotFoundError
        If the file does not exist.
    """
    try:
        from ase.io import read as ase_read  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "ASE is required for this reader.  Install it with:\n"
            "    pip install ase"
        ) from exc

    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Structure file not found: {filepath}")

    ase_atoms = ase_read(str(filepath), index=index)

    # Try to obtain stored charges
    try:
        stored_charges = ase_atoms.get_initial_charges()
    except Exception:
        stored_charges = None

    atoms: List[Atom] = []
    element_counts: Dict[str, int] = {}

    for i, ase_atom in enumerate(ase_atoms):
        elem = ase_atom.symbol

        if charges and elem in charges:
            q = float(charges[elem])
        elif stored_charges is not None:
            q = float(stored_charges[i])
        else:
            q = 0.0

        count = element_counts.get(elem, 0) + 1
        element_counts[elem] = count
        label = f"{prefix}{elem}{count}"

        atoms.append(
            Atom(
                element=elem,
                charge=q,
                position=np.array(ase_atom.position, dtype=float),
                label=label,
            )
        )

    return atoms


# ---------------------------------------------------------------------------
# 4. POSCAR convenience wrapper
# ---------------------------------------------------------------------------


def load_from_poscar(
    filepath: Union[str, Path],
    charges: Optional[Dict[str, float]] = None,
    prefix: str = "",
) -> List[Atom]:
    """
    Load atoms from a VASP POSCAR / CONTCAR file via ASE.

    Parameters
    ----------
    filepath : str or Path
    charges : dict {element: charge} or None
    prefix : str

    Returns
    -------
    list of Atom

    Raises
    ------
    ImportError  – ASE not installed.
    FileNotFoundError  – file not found.
    """
    return load_from_ase(filepath, charges=charges, prefix=prefix)


# ---------------------------------------------------------------------------
# 5. CIF convenience wrapper
# ---------------------------------------------------------------------------


def load_from_cif(
    filepath: Union[str, Path],
    charges: Optional[Dict[str, float]] = None,
    prefix: str = "",
) -> List[Atom]:
    """
    Load atoms from a CIF file via ASE.

    Crystallographic partial charges are rarely stored in CIF files.
    Supply them via the *charges* mapping or use the
    ``ions`` or ``BVS`` tools in pymatgen to compute approximate
    oxidation-state-derived charges before calling this function.

    Parameters
    ----------
    filepath : str or Path
    charges : dict {element: charge} or None
    prefix : str

    Returns
    -------
    list of Atom

    Raises
    ------
    ImportError  – ASE not installed.
    FileNotFoundError  – file not found.
    """
    return load_from_ase(filepath, charges=charges, prefix=prefix)


# ---------------------------------------------------------------------------
# 6. Pymatgen Structure reader (optional)
# ---------------------------------------------------------------------------


def load_from_pymatgen(
    filepath: Union[str, Path],
    use_oxidation_states: bool = True,
    charges: Optional[Dict[str, float]] = None,
    prefix: str = "",
) -> List[Atom]:
    """
    Load atoms from any pymatgen-supported structure file.

    When *use_oxidation_states* is ``True`` (default) pymatgen will attempt
    to decorate the structure with oxidation states using the ICSD-trained
    BVAnalyzer, and those values are used as partial charges.  Supply
    *charges* to override.

    Parameters
    ----------
    filepath : str or Path
    use_oxidation_states : bool
    charges : dict {element: charge} or None
    prefix : str

    Returns
    -------
    list of Atom

    Raises
    ------
    ImportError  – pymatgen not installed.
    FileNotFoundError  – file not found.
    """
    try:
        from pymatgen.core import Structure  # type: ignore
        from pymatgen.analysis.bond_valence import BVAnalyzer  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "pymatgen is required for this reader.  Install it with:\n"
            "    pip install pymatgen"
        ) from exc

    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Structure file not found: {filepath}")

    structure = Structure.from_file(str(filepath))

    if use_oxidation_states and charges is None:
        try:
            bva = BVAnalyzer()
            structure = bva.get_oxi_state_decorated_structure(structure)
        except Exception:
            pass  # BVAnalyzer may fail for some structures – carry on with 0

    atoms: List[Atom] = []
    element_counts: Dict[str, int] = {}

    for site in structure:
        elem = site.specie.symbol if hasattr(site.specie, "symbol") else str(site.specie)

        if charges and elem in charges:
            q = float(charges[elem])
        elif hasattr(site.specie, "oxi_state") and site.specie.oxi_state is not None:
            q = float(site.specie.oxi_state)
        else:
            q = 0.0

        # Pymatgen uses fractional coords – convert to Cartesian (Å)
        cart = structure.lattice.get_cartesian_coords(site.frac_coords)

        count = element_counts.get(elem, 0) + 1
        element_counts[elem] = count
        label = f"{prefix}{elem}{count}"

        atoms.append(
            Atom(element=elem, charge=q,
                 position=np.array(cart, dtype=float), label=label)
        )

    return atoms


# ---------------------------------------------------------------------------
# 7. Writer – custom XYZ with charges
# ---------------------------------------------------------------------------


def write_xyz(atoms: List[Atom], filepath: Union[str, Path]) -> None:
    """
    Write atoms to a 5-column custom XYZ file (element x y z charge).

    Parameters
    ----------
    atoms : list of Atom
    filepath : str or Path

    File format::

        <n_atoms>
        Generated by surface_dipole_library
        Si   0.000000   0.000000   0.000000   0.300000
        O    1.600000   0.000000   0.000000  -0.150000
        ...
    """
    filepath = Path(filepath)
    with open(filepath, "w") as fh:
        fh.write(f"{len(atoms)}\n")
        fh.write("Generated by surface_dipole_library\n")
        for atom in atoms:
            x, y, z = atom.position
            fh.write(
                f"{atom.element:<4s}  {x:12.6f}  {y:12.6f}  {z:12.6f}  {atom.charge:+.6f}\n"
            )
