# Scientific Walkthrough — Borosilicate Glass vs. TiO₂ Thin Film

This document traces every step the library executes internally, from raw input
atoms all the way to the final ranked interaction table and scientific
conclusions.  It uses the built-in test dataset
(`tests/test_glass_tio2.py`) as the running example.

To reproduce all numbers shown here:

```bash
python tests/test_glass_tio2.py
```

---

## Table of Contents

1. [Stage 1 — Input Data](#stage-1--input-data)
2. [Stage 2 — Dipole Moment of Each Surface](#stage-2--dipole-moment-of-each-surface)
3. [Stage 3 — Geometric Centroids](#stage-3--geometric-centroids)
4. [Stage 4 — Local Atomic Dipoles](#stage-4--local-atomic-dipoles)
5. [Stage 5 — Dipole–Dipole Energy for Every Pair](#stage-5--dipoledipole-energy-for-every-pair)
6. [Stage 6 — The Ranked Table](#stage-6--the-ranked-table)
7. [Stage 7 — Final Conclusions](#stage-7--final-conclusions)
8. [Geometry Diagram](#geometry-diagram)

---

## Stage 1 — Input Data

Two surfaces are defined in the **same Cartesian coordinate system**.  The z-axis
is perpendicular to the interface.  The glass surface occupies z ≈ 0–2.35 Å; the
TiO₂ film surface sits above it at z ≈ 3.50–5.80 Å.

### Borosilicate Glass Surface — 12 atoms

Partial charges are taken from the ClayFF / CHARMM force-field literature.

| Label | Element | Charge (e) | x (Å) | y (Å) | z (Å) | Role |
|-------|---------|-----------|-------|-------|-------|------|
| Si1_sub | Si | +0.310 | 0.00 | 0.00 | 0.00 | Tetrahedral Si centre |
| Si2_sub | Si | +0.310 | 5.06 | 0.00 | 0.00 | Tetrahedral Si centre |
| Si3_sub | Si | +0.310 | 2.53 | 4.38 | 0.00 | Tetrahedral Si centre |
| O_BO1_sub | O | −0.155 | 1.60 | 0.00 | 0.80 | Bridging oxygen (BO) |
| O_BO2_sub | O | −0.155 | 3.80 | 0.00 | 0.80 | Bridging oxygen (BO) |
| O_BO3_sub | O | −0.155 | 1.27 | 2.19 | 0.80 | Bridging oxygen (BO) |
| O_BO4_sub | O | −0.155 | 3.79 | 2.19 | 0.80 | Bridging oxygen (BO) |
| O_NBO1_sub | O | **−0.290** | 0.00 | 0.00 | 1.60 | **Non-bridging O (NBO)** |
| O_NBO2_sub | O | **−0.290** | 5.06 | 0.00 | 1.60 | **Non-bridging O (NBO)** |
| O_NBO3_sub | O | **−0.290** | 2.53 | 4.38 | 1.60 | **Non-bridging O (NBO)** |
| B1_sub | B | +0.270 | 2.53 | 1.46 | 0.00 | Boron (B₂O₃ component) |
| H_OH1_sub | H | +0.175 | 0.96 | 0.00 | 2.35 | Silanol –OH hydrogen |

**Net charge of glass surface:** Σqᵢ = **−0.115 e** (slightly anionic)

Key structural note: **Bridging oxygens (BO)** connect two Si tetrahedra and
carry a moderate charge of −0.155 e.  **Non-bridging oxygens (NBO)** terminate
the surface and carry a larger charge of −0.290 e — they are the most
electronegative atoms on the glass surface and will dominate attractive
interactions with the film.

---

### TiO₂ Film Surface — 11 atoms

Partial charges are from DFT-derived force fields (Matsui–Akaogi / ReaxFF).
All positions are shifted +3.5 Å in z above the glass.

| Label | Element | Charge (e) | x (Å) | y (Å) | z (Å) | Role |
|-------|---------|-----------|-------|-------|-------|------|
| Ti5c1_film | Ti | **+0.580** | 0.00 | 0.00 | 3.50 | **5-fold Ti (most reactive)** |
| Ti5c2_film | Ti | **+0.580** | 2.96 | 0.00 | 3.50 | **5-fold Ti (most reactive)** |
| Ti5c3_film | Ti | **+0.580** | 1.48 | 3.25 | 3.50 | **5-fold Ti (most reactive)** |
| Ti6c1_film | Ti | +0.480 | 1.48 | 1.48 | 4.50 | 6-fold Ti (bulk-like) |
| O_br1_film | O | −0.290 | 1.48 | 0.00 | 4.20 | Bridging O (2-fold) |
| O_br2_film | O | −0.290 | 4.44 | 0.00 | 4.20 | Bridging O (2-fold) |
| O_br3_film | O | −0.290 | 2.96 | 3.25 | 4.20 | Bridging O (2-fold) |
| O_ip1_film | O | −0.260 | 0.00 | 1.62 | 3.80 | In-plane O (3-fold) |
| O_ip2_film | O | −0.260 | 2.96 | 1.62 | 3.80 | In-plane O (3-fold) |
| O_OH1_film | O | −0.200 | 0.00 | 0.00 | 5.20 | Hydroxyl O (adsorbed) |
| H_OH1_film | H | +0.180 | 0.00 | 0.96 | 5.80 | Hydroxyl H (adsorbed) |

**Net charge of film surface:** Σqᵢ = **+0.810 e** (cationic)

Key structural note: The **5-fold coordinated Ti (Ti5c)** sites are
under-coordinated — they are missing one oxygen ligand compared to the bulk
octahedral environment.  This makes them strongly electron-deficient and the
primary adsorption sites on the rutile (110) surface.

---

## Stage 2 — Dipole Moment of Each Surface

### Formula

```
μ = Σᵢ qᵢ rᵢ        (units: e·Å)
```

Each atom contributes its partial charge multiplied by its position vector.
The result is a **3D vector** pointing in the direction of the net charge
displacement.

### Glass substrate dipole

Summing charge × position over all 12 atoms:

```
μx = (0.31)(0.00) + (0.31)(5.06) + (0.31)(2.53)
   + (-0.155)(1.60) + (-0.155)(3.80) + (-0.155)(1.27) + (-0.155)(3.79)
   + (-0.29)(0.00)  + (-0.29)(5.06)  + (-0.29)(2.53)
   + (0.27)(2.53) + (0.175)(0.96)
   = −0.6184 e·Å

μy = −0.1971 e·Å
μz = −1.4768 e·Å    ← dominant component
|μ| = 1.6131 e·Å  =  7.75 Debye
```

The large **negative z-component** means the glass dipole points downward —
electron density is concentrated in the NBO oxygens, which sit at the top
(z = 1.60 Å) of the glass surface layer.

### TiO₂ film dipole

```
μx = −0.0592 e·Å
μy = +0.9833 e·Å
μz = +2.6240 e·Å    ← dominant component
|μ| = 2.8028 e·Å  =  13.46 Debye
```

The large **positive z-component** means the film dipole points upward — the
positively charged Ti5c layer (z = 3.50 Å) sits below the negatively charged
bridging oxygen layer (z = 4.20 Å), so the positive end faces the glass.

### Physical interpretation of the two dipoles

```
          TiO₂ film surface
    ─────────────────────────────
    [−][−][−]  O_br  z = 4.20 Å    ↑ Film dipole points UP (+z)
    [+][+][+]  Ti5c  z = 3.50 Å
    ─────────────────────────────    ← interface gap ~1.9 Å
    [−][−][−]  O_NBO z = 1.60 Å    ↓ Glass dipole points DOWN (−z)
    [+][+][+]  Si    z = 0.00 Å
    ─────────────────────────────
          Borosilicate glass
```

The glass dipole (pointing down, −z) and the film dipole (pointing up, +z)
are **anti-parallel** — they attract each other just as two bar magnets held
N-to-S attract.  This geometric alignment is why this glass–TiO₂ pair is a
well-known compatible interface system.

---

## Stage 3 — Geometric Centroids

Before computing per-atom local dipoles, the library calculates the
**geometric centroid** (unweighted mean position) of each surface group:

```
r_centroid = (1/N) × Σᵢ rᵢ
```

```
Glass centroid  = [2.4275, 1.2167, 0.8625] Å
Film centroid   = [1.6145, 1.1073, 4.2000] Å
```

The centroid serves as the **coordinate origin** for local atomic dipoles.
This makes all subsequent calculations independent of where the user places the
global origin — moving both surfaces together by any vector will not change any
interaction energy.

---

## Stage 4 — Local Atomic Dipoles

### Formula

```
μᵢ(local) = qᵢ × (rᵢ − r_centroid)
```

This gives each atom a dipole vector that represents its contribution to the
total group dipole.  For a charge-neutral group, the sum of all local atomic
dipoles equals the total group dipole exactly.

### Calculated values for key atoms

| Atom | Charge (e) | μ_local (e·Å) | |μ_local| (e·Å) | Physical meaning |
|------|-----------|--------------|--------------|-----------------|
| O_NBO1_sub | −0.290 | [+0.704, +0.353, −0.214] | **0.816** | Largest glass contributor — high charge, displaced from centroid |
| Si1_sub | +0.310 | [−0.753, −0.377, −0.267] | 0.883 | Points opposite to O_NBO |
| O_BO1_sub | −0.155 | [+0.128, +0.189, +0.010] | 0.228 | Smaller — lower charge |
| H_OH1_sub | +0.175 | [−0.257, −0.213, +0.260] | 0.423 | Small but sits high (z=2.35) |
| Ti5c1_film | +0.580 | [−0.936, −0.642, −0.406] | **1.206** | Largest film contributor — highest charge |
| O_br1_film | −0.290 | [+0.039, +0.321,  0.000] | 0.324 | Moderate — near centroid in z |
| O_ip1_film | −0.260 | [+0.420, −0.133, +0.104] | 0.453 | Moderate |

**O_NBO1 and Ti5c1 have the largest local dipole magnitudes** in their
respective groups.  They are the atoms that will produce the strongest
interaction signal in the pairwise table — exactly what Stage 6 confirms.

---

## Stage 5 — Dipole–Dipole Energy for Every Pair

### Formula

```
U = (1/4πε₀) [ (μ₁·μ₂)/r³  −  3(μ₁·r)(μ₂·r)/r⁵ ]
```

In practical units (μ in e·Å, r in Å, U in eV):

```
U = 14.3996 × [ (μ₁·μ₂)/r³  −  3(μ₁·r)(μ₂·r)/r⁵ ]
```

where 14.3996 is the Coulomb constant k_e expressed in eV·Å/e².

The library uses `itertools.product` to enumerate all **12 × 11 = 132 pairs**
and applies this formula to each one.

---

### Hand-trace: Rank-1 Pair — O_NBO1_sub ↔ Ti5c1_film

```
Atoms:
  O_NBO1_sub   position = [0.00, 0.00, 1.60] Å    charge = −0.290 e
  Ti5c1_film   position = [0.00, 0.00, 3.50] Å    charge = +0.580 e

Step A — displacement vector r (from O to Ti):
  r_vec = [0.00, 0.00, 3.50] − [0.00, 0.00, 1.60] = [0.00, 0.00, 1.90] Å
  |r|   = 1.90 Å

Step B — local dipoles (from Stage 4):
  μ₁ (O_NBO1) = [+0.7040, +0.3528, −0.2139] e·Å
  μ₂ (Ti5c1)  = [−0.9364, −0.6422, −0.4060] e·Å

Step C — dot products:
  μ₁·μ₂ = (0.7040)(−0.9364) + (0.3528)(−0.6422) + (−0.2139)(−0.4060)
         = −0.6592 + (−0.2266) + 0.0868
         = −0.7990  e²·Å²     ← negative: dipoles oppose each other

  μ₁·r  = (0.7040)(0) + (0.3528)(0) + (−0.2139)(1.90)
         = −0.4064  e·Å²

  μ₂·r  = (−0.9364)(0) + (−0.6422)(0) + (−0.4060)(1.90)
         = −0.7714  e·Å²

Step D — energy terms:
  Term1 = μ₁·μ₂ / r³ = −0.7990 / (1.90)³ = −0.7990 / 6.859 = −0.1165 e²/Å

  Term2 = 3 × (μ₁·r)(μ₂·r) / r⁵
        = 3 × (−0.4064)(−0.7714) / (1.90)⁵
        = 3 × 0.3135 / 24.761
        = +0.0380 e²/Å

Step E — final energy:
  U = 14.3996 × (−0.1165 − 0.0380)
    = 14.3996 × (−0.1545)
    = −2.224 eV    ✔  STRONGLY ATTRACTIVE
```

Why is this pair so dominant?  Three compounding reasons:
1. **Highest charges**: O_NBO at −0.290 e and Ti5c at +0.580 e are the most
   charged atoms in each group.
2. **Shortest distance**: 1.90 Å is the minimum separation across all 132 pairs.
   Since energy scales as 1/r³, this alone multiplies strength by 5× compared
   to a 3 Å pair.
3. **Aligned geometry**: Both atoms sit on the z-axis, maximising the
   angular projection of the dipoles onto the inter-atom vector.

---

### Hand-trace: Rank-132 Pair — O_NBO2_sub ↔ O_br2_film (most repulsive)

```
  O_NBO2_sub  charge = −0.290 e   position = [5.06, 0.00, 1.60] Å
  O_br2_film  charge = −0.290 e   position = [4.44, 0.00, 4.20] Å

  |r| = 2.67 Å
  Both atoms are strongly negative → local dipoles point in the same
  direction → μ₁·μ₂ > 0 → Term1 is positive → repulsive.

  U = +0.570 eV    ✔  REPULSIVE
```

---

## Stage 6 — The Ranked Table

All 132 interaction energies are sorted ascending (most negative first).
Results: **67 attractive pairs (50.8%)** and **65 repulsive pairs (49.2%)**.

### Top 10 — Strongest Attractive Interactions

| Rank | Substrate Atom | Film Atom | Distance (Å) | Energy (eV) | Type |
|------|---------------|-----------|-------------|-------------|------|
| 1 | **O_NBO1_sub** | **Ti5c1_film** | 1.90 | **−2.2243** | attractive |
| 2 | O_NBO3_sub | Ti5c3_film | 2.45 | −0.3509 | attractive |
| 3 | H_OH1_sub | Ti5c1_film | 1.50 | −0.1875 | attractive |
| 4 | H_OH1_sub | O_br1_film | 1.92 | −0.1707 | attractive |
| 5 | Si2_sub | O_br2_film | 4.25 | −0.1227 | attractive |
| 6 | O_NBO1_sub | Ti5c3_film | 4.05 | −0.1217 | attractive |
| 7 | O_BO3_sub | Ti5c3_film | 2.91 | −0.1162 | attractive |
| 8 | O_BO1_sub | Ti5c1_film | 3.14 | −0.1040 | attractive |
| 9 | Si2_sub | Ti5c2_film | 4.08 | −0.1000 | attractive |
| 10 | O_BO2_sub | Ti5c2_film | 2.83 | −0.0996 | attractive |

### Bottom 5 — Strongest Repulsive Interactions

| Rank | Substrate Atom | Film Atom | Distance (Å) | Energy (eV) | Type |
|------|---------------|-----------|-------------|-------------|------|
| 128 | O_NBO1_sub | O_ip1_film | 2.73 | +0.1594 | repulsive |
| 129 | O_NBO2_sub | Ti5c2_film | 2.83 | +0.2178 | repulsive |
| 130 | Si1_sub | Ti5c1_film | 3.50 | +0.2451 | repulsive |
| 131 | O_NBO3_sub | O_br3_film | 2.87 | +0.2996 | repulsive |
| **132** | **O_NBO2_sub** | **O_br2_film** | 2.67 | **+0.5704** | repulsive |

---

## Stage 7 — Final Conclusions

### Conclusion 1 — The dominant interaction is O_NBO ↔ Ti5c

The non-bridging oxygen on the glass surface and the 5-fold Ti site on TiO₂
form the **single strongest pair in the entire system** at **−2.224 eV**.
This is 6.3× stronger than the next-best pair (−0.351 eV).  This pair
should be the primary target for experimental interface engineering —
any treatment that increases NBO density on the glass surface
(e.g. alkali leaching, etching) or Ti5c density on the film
(e.g. reduced-pressure deposition) will directly strengthen adhesion.

### Conclusion 2 — Ti5c sites are the film's primary bonding anchors

Ranks 1, 2, 6, 7, 8, 9, 10 — seven of the top ten pairs — involve a Ti5c
site.  The 6-fold Ti (Ti6c) does not appear in the top 10 at all.
This confirms that the under-coordinated surface Ti is the active site for
substrate binding, consistent with DFT and STM studies of TiO₂(110).

### Conclusion 3 — NBO oxygens on glass are the preferred docking sites

Ranks 1, 2, 6 all involve NBO oxygens.  With a charge of −0.290 e (vs.
−0.155 e for bridging oxygens), they produce nearly twice the local dipole
strength.  For glass surface preparation, maximising the NBO fraction
(e.g. by reducing the B₂O₃ content which converts NBO to BO) should
improve adhesion to TiO₂ films.

### Conclusion 4 — Surface hydroxyl groups enhance adhesion

Ranks 3 and 4 involve the silanol hydrogen H_OH1 attracting both Ti5c
(−0.188 eV) and a bridging oxygen on the film (−0.171 eV).  This predicts
that **surface hydroxylation of glass** — which is common in humid
environments and after wet cleaning — does not harm adhesion; it actively
contributes two additional attractive pathways.

### Conclusion 5 — Same-sign pairs are the interface's weak points

The worst pair (O_NBO2 ↔ O_br2, +0.570 eV) is oxygen-to-oxygen at close
range.  Similarly, Si1 ↔ Ti5c1 (cation–cation, rank 130, +0.245 eV) is
strongly repulsive.  These pairs arise when the crystal lattices of the two
surfaces are misregistered — an O row on the glass aligns with an O row on
the film, or a Si site aligns with a Ti site.  This suggests that **lattice
matching and in-plane rotation** of the film during deposition should be
optimised to minimise these repulsive configurations.

### Conclusion 6 — Overall compatibility is confirmed but geometry-sensitive

```
Total pairs:       132  (12 glass atoms × 11 film atoms)
Attractive (U<0):   67  (50.8%)
Repulsive  (U>0):   65  (49.2%)

Strongest attraction:  −2.224 eV   O_NBO1_sub – Ti5c1_film
Strongest repulsion:   +0.570 eV   O_NBO2_sub – O_br2_film
```

The interface is not uniformly attractive.  Exactly half the pairs are
repulsive.  The **net interaction is dominated by the rank-1 pair** which is
4× larger in magnitude than the strongest repulsion.  The glass–TiO₂ system
is compatible, but the strength of adhesion is highly sensitive to the
spatial registry between the two lattices.  This is precisely the value of
this screening tool: it identifies not just whether two materials are
compatible, but **which specific atom pairs drive adhesion** — information
that guides both deposition conditions and surface pre-treatments before any
expensive DFT simulation is run.

---

## Geometry Diagram

```
z (Å)
 6.0  ─  H_OH1_film   (+0.18 e)  ← adsorbed hydroxyl
 5.2  ─  O_OH1_film   (−0.20 e)
         ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  TiO₂ film surface
 4.5  ─  Ti6c1_film   (+0.48 e)  bulk-like Ti
 4.2  ─  O_br_film    (−0.29 e)  bridging O row         ↑
 3.8  ─  O_ip_film    (−0.26 e)  in-plane O             |  Film dipole
 3.5  ─  Ti5c_film    (+0.58 e)  ← primary bonding site |  points up (+z)

         ════════════ interface gap ≈ 1.9 Å ════════════

 1.6  ─  O_NBO_sub    (−0.29 e)  ← primary docking site |  Glass dipole
 0.8  ─  O_BO_sub     (−0.155 e) bridging O             |  points down (−z)
 0.0  ─  Si_sub / B   (+0.31 e)  Si tetrahedral centres ↓
         ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  Glass surface (bulk below)

The two dipoles are anti-parallel → they attract.
The O_NBO – Ti5c gap (1.90 Å) is the shortest cross-interface distance
and produces the dominant interaction at −2.224 eV.
```

---

*Generated by surface_dipole_library v1.0.0*
