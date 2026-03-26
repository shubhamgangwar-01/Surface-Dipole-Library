# Atom Label Glossary

This document explains how to read every atom label that appears in the
ranked interaction table produced by `analyze_surface_interactions()`.

---

## Label Structure

Every atom label follows this pattern:

```
  O_NBO1_sub
  │  │   │  └── _sub  → belongs to the SUBstrate (glass)
  │  │   └───── 1     → atom number (makes it unique)
  │  └───────── NBO   → chemical role: Non-Bridging Oxygen
  └──────────── O     → element symbol: Oxygen

  Ti5c1_film
  │  │  │  └── _film → belongs to the FILM (TiO₂)
  │  │  └───── 1     → atom number
  │  └──────── 5c    → coordination: 5-fold coordinated
  └──────────── Ti   → element symbol: Titanium
```

---

## Glass Substrate Atoms (`_sub`)

| Label | Element | Charge (e) | z (Å) | Meaning |
|-------|---------|-----------|-------|---------|
| `Si1_sub`, `Si2_sub`, `Si3_sub` | Silicon | +0.310 | 0.00 | Centre of a SiO₄ tetrahedron. Three of them tile the glass surface. |
| `O_BO1_sub` → `O_BO4_sub` | Oxygen | −0.155 | 0.80 | **B**ridging **O**xygen — connects two Si tetrahedra. Moderately negative. Sits mid-layer. |
| `O_NBO1_sub` → `O_NBO3_sub` | Oxygen | −0.290 | 1.60 | **N**on-**B**ridging **O**xygen — attached to only one Si, dangling at the surface. Most negative atom on glass. Sits at the very top of the glass layer. |
| `B1_sub` | Boron | +0.270 | 0.00 | Boron from the B₂O₃ component of borosilicate glass. |
| `H_OH1_sub` | Hydrogen | +0.175 | 2.35 | H of a surface silanol (Si–OH) group. Forms when glass is exposed to moisture. Sits highest on the glass. |

**Key point:** NBO oxygens are the most important atoms on the glass side.
They carry the highest negative charge (−0.290 e vs −0.155 e for bridging
oxygens) and sit closest to the film, making them the dominant docking sites.

---

## TiO₂ Film Atoms (`_film`)

| Label | Element | Charge (e) | z (Å) | Meaning |
|-------|---------|-----------|-------|---------|
| `Ti5c1_film` → `Ti5c3_film` | Titanium | +0.580 | 3.50 | **5-fold c**oordinated Ti — missing one oxygen ligand vs. bulk. Most reactive, most electron-hungry site on the TiO₂ surface. Highest positive charge. |
| `Ti6c1_film` | Titanium | +0.480 | 4.50 | **6-fold c**oordinated Ti — fully surrounded by oxygens, bulk-like. Less reactive. |
| `O_br1_film` → `O_br3_film` | Oxygen | −0.290 | 4.20 | **Br**idging oxygen row — sits between two Ti atoms, forming the characteristic rows on the rutile (110) surface. |
| `O_ip1_film`, `O_ip2_film` | Oxygen | −0.260 | 3.80 | **I**n-**p**lane oxygen — lies in the same plane as the Ti atoms, 3-fold coordinated. |
| `O_OH1_film` | Oxygen | −0.200 | 5.20 | Oxygen of an OH group adsorbed on Ti5c in humid conditions. |
| `H_OH1_film` | Hydrogen | +0.180 | 5.80 | Hydrogen of that same adsorbed OH group. |

**Key point:** Ti5c sites are the most important atoms on the film side.
They are under-coordinated (missing one O ligand) and actively seek negative
charge from the glass surface — making them the primary bonding anchors.

---

## Why the Top-Ranked Pairs Win

### Rank 1 — `O_NBO1_sub` ↔ `Ti5c1_film`  (−2.224 eV)

```
  O_NBO1_sub  →  Most negative atom on glass  (−0.290 e)  at z = 1.60 Å
  Ti5c1_film  →  Most positive atom on film   (+0.580 e)  at z = 3.50 Å
  Gap = 1.90 Å  ← shortest cross-interface distance
```

Three factors compound: highest opposite charges + shortest distance +
dipoles pointing toward each other. This makes it 6× stronger than rank 2.

---

### Rank 2 — `O_NBO3_sub` ↔ `Ti5c3_film`  (−0.351 eV)

Same atom types as rank 1 (NBO oxygen ↔ Ti5c) but at a larger separation
(2.45 Å) because they are the third copies of each atom, positioned at the
far corner of the surface tile.

---

### Rank 3 — `H_OH1_sub` ↔ `Ti5c1_film`  (−0.188 eV)

```
  H_OH1_sub   →  Silanol hydrogen on glass  (+0.175 e)  at z = 2.35 Å
  Ti5c1_film  →  Same hungry Ti5c           (+0.580 e)  at z = 3.50 Å
  Gap = 1.50 Å  ← even closer than rank 1
```

Despite the shorter distance, the energy is weaker than rank 1 because H has
a much smaller partial charge and local dipole than O_NBO. This also shows
that **surface hydroxylation of glass enhances adhesion** — the silanol H
provides an additional attractive pathway to the film.

---

### Rank 4 — `H_OH1_sub` ↔ `O_br1_film`  (−0.171 eV)

The silanol H on glass is also attracted to the bridging oxygen row on the
film. This is a hydrogen-bond-like interaction across the interface.

---

## Most Repulsive Pair — `O_NBO2_sub` ↔ `O_br2_film`  (+0.570 eV)

```
  O_NBO2_sub  →  Negative oxygen on glass  (−0.290 e)
  O_br2_film  →  Negative oxygen on film   (−0.290 e)
  Both negative → same-sign local dipoles → repulsive
```

This occurs when the O row on the glass aligns with the O row on the film —
a misregistered interface. Optimising the in-plane rotation of the film
during deposition avoids this configuration.

---

## Quick Reference

```
Suffix   Meaning
──────   ───────────────────────────────────────────────
_sub     atom belongs to the substrate (glass)
_film    atom belongs to the thin film (TiO₂)

Prefix   Meaning
──────   ───────────────────────────────────────────────
O_NBO    Non-Bridging Oxygen  — most negative, best docking site on glass
O_BO     Bridging Oxygen      — moderate charge, connects two Si
Ti5c     5-fold Ti            — most positive, primary anchor on TiO₂ film
Ti6c     6-fold Ti            — bulk-like, less reactive
O_br     Bridging O on TiO₂  — forms rows on rutile (110) surface
O_ip     In-plane O on TiO₂  — 3-fold coordinated
O_OH     Hydroxyl O           — from adsorbed water molecule
H_OH     Hydroxyl H           — from silanol (glass) or adsorbed OH (film)
Si       Silicon              — tetrahedral centre of glass network
B        Boron                — from B₂O₃ component of borosilicate
```

---

*surface_dipole_library v1.0.0*
