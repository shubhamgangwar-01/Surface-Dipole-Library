"""
interaction.py
--------------
Dipole–dipole interaction energy calculator for the surface_dipole_library.

Physical formula
~~~~~~~~~~~~~~~~
The interaction energy between two point dipoles mu1 and mu2
separated by displacement vector r is:

    U = (1 / 4*pi*eps0) [ mu1.mu2 / r^3  -  3 (mu1.r)(mu2.r) / r^5 ]

Unit system used here
~~~~~~~~~~~~~~~~~~~~~
    Charges   – elementary charge  e
    Distances – Angstrom           Å
    Dipoles   – e·Å
    Energy    – electron-volt      eV

The Coulomb prefactor in these units:
    k_e = e^2 / (4*pi*eps0 * 1 Å) = 14.3996 eV·Å / e^2

Sign convention
~~~~~~~~~~~~~~~
    U < 0  →  attractive  (energetically favourable)
    U > 0  →  repulsive   (energetically unfavourable)
"""

from __future__ import annotations

from typing import Dict, Any

import numpy as np

from .atoms import Atom
from .geometry import displacement_vector
from .dipole import atomic_local_dipole


# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------

# Coulomb constant in practical surface-science units:
#   k_e * e^2 / Å = 14.3996 eV
# Derivation:
#   k_e = 8.987551787e9 N·m²/C²
#   e   = 1.602176634e-19 C
#   1 Å = 1e-10 m
#   1 eV = 1.602176634e-19 J
#   k_e * e^2 / Å = 8.9876e9 * (1.6022e-19)^2 / 1e-10 J = 2.3071e-18 J = 14.3996 eV
K_E: float = 14.3996  # eV·Å / e^2

# Minimum physical separation allowed between two atoms
MIN_DISTANCE: float = 0.5  # Å


# ---------------------------------------------------------------------------
# Core physics
# ---------------------------------------------------------------------------


def dipole_dipole_energy(
    mu1: np.ndarray,
    mu2: np.ndarray,
    r_vec: np.ndarray,
) -> float:
    """
    Calculate dipole–dipole interaction energy.

        U = K_e * [ (mu1·mu2) / r^3  -  3*(mu1·r)*(mu2·r) / r^5 ]

    Parameters
    ----------
    mu1 : array-like (3,)
        Dipole moment of group/atom 1, in e·Å.
    mu2 : array-like (3,)
        Dipole moment of group/atom 2, in e·Å.
    r_vec : array-like (3,)
        Displacement vector from atom1 to atom2, in Å.

    Returns
    -------
    float
        Interaction energy in eV.  Negative = attractive.

    Raises
    ------
    ValueError
        If |r_vec| < MIN_DISTANCE (non-physical overlap).
    """
    mu1 = np.asarray(mu1, dtype=float)
    mu2 = np.asarray(mu2, dtype=float)
    r_vec = np.asarray(r_vec, dtype=float)

    r = float(np.linalg.norm(r_vec))

    if r < MIN_DISTANCE:
        raise ValueError(
            f"Atom separation {r:.4f} Å is below minimum allowed "
            f"{MIN_DISTANCE} Å. Check input coordinates."
        )

    # Trivial case – both dipoles vanish
    if np.linalg.norm(mu1) < 1e-15 and np.linalg.norm(mu2) < 1e-15:
        return 0.0

    mu1_dot_mu2 = float(np.dot(mu1, mu2))
    mu1_dot_r   = float(np.dot(mu1, r_vec))
    mu2_dot_r   = float(np.dot(mu2, r_vec))

    term1 = mu1_dot_mu2 / (r ** 3)
    term2 = 3.0 * mu1_dot_r * mu2_dot_r / (r ** 5)

    return float(K_E * (term1 - term2))


# ---------------------------------------------------------------------------
# Atom-pair wrapper
# ---------------------------------------------------------------------------


def atom_pair_interaction(
    atom1: Atom,
    atom2: Atom,
    centroid1: np.ndarray,
    centroid2: np.ndarray,
) -> Dict[str, Any]:
    """
    Compute the dipole–dipole interaction between two surface atoms.

    Each atom's effective local dipole is computed relative to the
    geometric centroid of its parent group:

        mu_i = q_i * (r_i - r_centroid)

    Parameters
    ----------
    atom1 : Atom
        Substrate atom.
    atom2 : Atom
        Film atom.
    centroid1 : ndarray (3,)
        Geometric centroid of the substrate surface group (Å).
    centroid2 : ndarray (3,)
        Geometric centroid of the film surface group (Å).

    Returns
    -------
    dict with keys:
        atom1, atom2, distance, r_vec,
        mu1, mu2, mu1_magnitude, mu2_magnitude,
        interaction_energy, interaction_type,
        substrate_charge, film_charge
    """
    r_vec = displacement_vector(atom1, atom2)
    r     = float(np.linalg.norm(r_vec))

    mu1 = atomic_local_dipole(atom1, centroid1)
    mu2 = atomic_local_dipole(atom2, centroid2)

    energy = dipole_dipole_energy(mu1, mu2, r_vec)

    return {
        "atom1":              atom1,
        "atom2":              atom2,
        "distance":           r,
        "r_vec":              r_vec,
        "mu1":                mu1,
        "mu2":                mu2,
        "mu1_magnitude":      float(np.linalg.norm(mu1)),
        "mu2_magnitude":      float(np.linalg.norm(mu2)),
        "interaction_energy": energy,
        "interaction_type":   interaction_type(energy),
        "substrate_charge":   atom1.charge,
        "film_charge":        atom2.charge,
    }


def interaction_type(energy: float, threshold: float = 0.0) -> str:
    """
    Classify an interaction energy as attractive, repulsive, or neutral.

    Parameters
    ----------
    energy : float  (eV)
    threshold : float
        Half-width of the neutral band around zero (default 0.0).

    Returns
    -------
    str  –  "attractive", "repulsive", or "neutral"
    """
    if abs(energy) <= threshold:
        return "neutral"
    return "attractive" if energy < 0.0 else "repulsive"
