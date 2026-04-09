# Surface Dipole Library — Step-by-Step Walkthrough

A complete pen-and-paper walkthrough of the `surface_dipole_library` using a
concrete example: **4 substrate atoms** and **3 film atoms**.

---

## The Setup

**4 substrate atoms** (the glass/TiO₂ surface, sitting at z = 0):

| Label    | Element | Charge (e) | Position [x, y, z] (Å) |
|----------|---------|-----------|------------------------|
| sub_Si1  | Si      | +0.40     | [0.0, 0.0, 0.0]        |
| sub_O1   | O       | −0.20     | [1.5, 0.0, 0.0]        |
| sub_O2   | O       | −0.20     | [0.0, 1.5, 0.0]        |
| sub_Ti1  | Ti      | +0.30     | [1.5, 1.5, 0.0]        |

**3 film atoms** (the ITO / deposited layer, floating ~4 Å above):

| Label     | Element | Charge (e) | Position [x, y, z] (Å) |
|-----------|---------|-----------|------------------------|
| film_In1  | In      | +0.30     | [0.5, 0.5, 4.0]        |
| film_O3   | O       | −0.20     | [1.0, 0.5, 4.5]        |
| film_O4   | O       | −0.15     | [0.5, 1.0, 4.5]        |

---

## STEP 1 — Building the dicts and converting to `Atom` objects

You start with plain Python dicts:

```python
substrate_raw = [
    {"element": "Si", "charge": +0.40, "position": [0.0, 0.0, 0.0]},
    {"element": "O",  "charge": -0.20, "position": [1.5, 0.0, 0.0]},
    {"element": "O",  "charge": -0.20, "position": [0.0, 1.5, 0.0]},
    {"element": "Ti", "charge": +0.30, "position": [1.5, 1.5, 0.0]},
]

film_raw = [
    {"element": "In", "charge": +0.30, "position": [0.5, 0.5, 4.0]},
    {"element": "O",  "charge": -0.20, "position": [1.0, 0.5, 4.5]},
    {"element": "O",  "charge": -0.15, "position": [0.5, 1.0, 4.5]},
]
```

`atoms_from_dicts(substrate_raw, prefix="sub_")` loops over each dict and calls
`Atom.from_dict()`. Inside `Atom.__post_init__`, the `position` list is
immediately converted to a NumPy array. Because the element `"O"` appears twice,
the function auto-labels them `sub_O1` and `sub_O2`. Final objects:

```
Atom(label='sub_Si1', element='Si', charge=+0.4000, position=[0.0, 0.0, 0.0] Å)
Atom(label='sub_O1',  element='O',  charge=-0.2000, position=[1.5, 0.0, 0.0] Å)
Atom(label='sub_O2',  element='O',  charge=-0.2000, position=[0.0, 1.5, 0.0] Å)
Atom(label='sub_Ti1', element='Ti', charge=+0.3000, position=[1.5, 1.5, 0.0] Å)
```

Same thing for film atoms with prefix `"film_"`.

**Conclusion:** Every atom now carries its element name, a partial charge (how
much electron charge it holds), and a 3D location in space (Å).

---

## STEP 2 — `calculate_dipole()` on the substrate group

**Formula:**  μ = Σᵢ qᵢ rᵢ

Multiply each atom's charge by its position vector, then sum:

```
μ_sub = (+0.40) × [0.0, 0.0, 0.0]   =  [ 0.000,  0.000,  0.000]
      + (−0.20) × [1.5, 0.0, 0.0]   =  [−0.300,  0.000,  0.000]
      + (−0.20) × [0.0, 1.5, 0.0]   =  [ 0.000, −0.300,  0.000]
      + (+0.30) × [1.5, 1.5, 0.0]   =  [+0.450, +0.450,  0.000]
                                        ─────────────────────────
      μ_sub                          =  [+0.150, +0.150,  0.000]  e·Å
```

```
|μ_sub| = √(0.15² + 0.15²) = √0.045 ≈ 0.2121 e·Å
        = 0.2121 × 4.803 ≈ 1.019 Debye

Net charge Q_sub = +0.40 − 0.20 − 0.20 + 0.30 = +0.30 e
```

**Conclusion:** The substrate group has a net positive charge (+0.30 e). Its
total dipole moment points equally in the +x and +y directions, meaning the
positive charges (Si, Ti) are displaced toward those directions relative to the
negative oxygens. The z-component is zero because everything is flat at z = 0.

---

## STEP 3 — `calculate_dipole()` on the film group

```
μ_film = (+0.30) × [0.5, 0.5, 4.0]   =  [+0.150, +0.150, +1.200]
       + (−0.20) × [1.0, 0.5, 4.5]   =  [−0.200, −0.100, −0.900]
       + (−0.15) × [0.5, 1.0, 4.5]   =  [−0.075, −0.150, −0.675]
                                         ─────────────────────────
       μ_film                         =  [−0.125, −0.100, −0.375]  e·Å
```

```
|μ_film| = √(0.125² + 0.100² + 0.375²) = √0.1663 ≈ 0.4078 e·Å
         = 0.4078 × 4.803 ≈ 1.959 Debye

Net charge Q_film = +0.30 − 0.20 − 0.15 = −0.05 e
```

**Conclusion:** The film is nearly charge-neutral (only −0.05 e net). Its dipole
is mainly in the −z direction (pointing downward, toward the substrate), because
the In atom sits 0.5 Å below the two oxygens and pulls positive charge downward.

---

## STEP 4 — `calculate_centroid()` — the geometric centre of each group

This is simply the unweighted mean of all positions:

```
r_c_sub = ([0.0,0.0,0.0] + [1.5,0.0,0.0] + [0.0,1.5,0.0] + [1.5,1.5,0.0]) / 4
         = [3.0, 3.0, 0.0] / 4
         = [0.75, 0.75, 0.00]  Å

r_c_film = ([0.5,0.5,4.0] + [1.0,0.5,4.5] + [0.5,1.0,4.5]) / 3
          = [2.0, 2.0, 13.0] / 3
          = [0.667, 0.667, 4.333]  Å
```

**Why do we need centroids?** The library needs a single reference point for
each layer so it can define where each atom sits *relative to its own group*.
Think of it like a centre-of-mass — except purely geometric, ignoring charge
weights. The centroid is the "home base" for each surface layer, and it is used
exclusively to compute local dipoles in the next step.

---

## STEP 5 — `atomic_local_dipole()` — each atom's contribution relative to the centroid

**Formula:** μᵢ = qᵢ × (rᵢ − r_centroid)

This shifts the origin to the centroid so each atom's local dipole reflects
where it sits *within* its own layer.

### Substrate atoms (centroid = [0.75, 0.75, 0.00]):

```
μ_Si1 = (+0.40) × ([0.00, 0.00, 0.00] − [0.75, 0.75, 0.00])
       = (+0.40) × [−0.75, −0.75, 0.00]
       = [−0.300, −0.300,  0.000]  e·Å

μ_O1  = (−0.20) × ([1.50, 0.00, 0.00] − [0.75, 0.75, 0.00])
       = (−0.20) × [+0.75, −0.75, 0.00]
       = [−0.150, +0.150,  0.000]  e·Å

μ_O2  = (−0.20) × ([0.00, 1.50, 0.00] − [0.75, 0.75, 0.00])
       = (−0.20) × [−0.75, +0.75, 0.00]
       = [+0.150, −0.150,  0.000]  e·Å

μ_Ti1 = (+0.30) × ([1.50, 1.50, 0.00] − [0.75, 0.75, 0.00])
       = (+0.30) × [+0.75, +0.75, 0.00]
       = [+0.225, +0.225,  0.000]  e·Å
```

### Film atoms (centroid = [0.667, 0.667, 4.333]):

```
μ_In1 = (+0.30) × ([0.50, 0.50, 4.00] − [0.667, 0.667, 4.333])
       = (+0.30) × [−0.167, −0.167, −0.333]
       = [−0.050, −0.050, −0.100]  e·Å

μ_O3  = (−0.20) × ([1.00, 0.50, 4.50] − [0.667, 0.667, 4.333])
       = (−0.20) × [+0.333, −0.167, +0.167]
       = [−0.067, +0.033, −0.033]  e·Å

μ_O4  = (−0.15) × ([0.50, 1.00, 4.50] − [0.667, 0.667, 4.333])
       = (−0.15) × [−0.167, +0.333, +0.167]
       = [+0.025, −0.050, −0.025]  e·Å
```

**Conclusion:** Every atom now has its own "local dipole" — a small vector that
says: "given my charge and how far I sit from my layer's centre, this is how
much I personally contribute to the layer's polarity." These local dipoles are
the building blocks for the interaction energy calculation.

---

## STEP 6 — `generate_all_pairs()` — the Cartesian product

The code uses `itertools.product(substrate_atoms, film_atoms)` which gives every
possible pairing:

```
(sub_Si1, film_In1)   (sub_Si1, film_O3)   (sub_Si1, film_O4)
(sub_O1,  film_In1)   (sub_O1,  film_O3)   (sub_O1,  film_O4)
(sub_O2,  film_In1)   (sub_O2,  film_O3)   (sub_O2,  film_O4)
(sub_Ti1, film_In1)   (sub_Ti1, film_O3)   (sub_Ti1, film_O4)
```

That is **4 × 3 = 12 pairs**. For each pair the code first checks the
atom-to-atom distance. If a cutoff is set (say 8 Å) and the distance exceeds
it, the pair is skipped silently. Otherwise it calls `atom_pair_interaction()`.

---

## STEP 7 — `dipole_dipole_energy()` — the actual physics calculation

**Full formula:**

```
U = K_e × [ (μ₁ · μ₂) / r³  −  3 (μ₁ · r̂)(μ₂ · r̂) / r⁵ ]
```

where `K_e = 14.3996 eV·Å / e²` (Coulomb constant in surface-science units).

Two pairs are worked out in full below to illustrate attraction vs repulsion.

---

### Pair A: sub_Ti1 ↔ film_O3 — opposite charges → attractive

**Step 7a — displacement vector r_vec** (from sub_Ti1 to film_O3):

```
r_vec = r_O3 − r_Ti1 = [1.0, 0.5, 4.5] − [1.5, 1.5, 0.0]
      = [−0.5, −1.0, +4.5]  Å
```

**Step 7b — scalar distance r:**

```
r = √(0.5² + 1.0² + 4.5²) = √(0.25 + 1.00 + 20.25) = √21.50 ≈ 4.637 Å
```

This is the actual atom-to-atom separation in 3D space — the r used in the
denominator of the energy formula.

**Step 7c — local dipoles** (from Step 5):

```
μ₁  =  μ_Ti1  =  [+0.225, +0.225, 0.000]  e·Å
μ₂  =  μ_O3   =  [−0.067, +0.033, −0.033]  e·Å
```

**Step 7d — the three dot products:**

```
μ₁ · μ₂  = (0.225)(−0.067) + (0.225)(+0.033) + (0)(−0.033)
           = −0.01508 + 0.00750 + 0
           = −0.00758  e²·Å²

μ₁ · r_vec = (0.225)(−0.5) + (0.225)(−1.0) + (0)(4.5)
            = −0.1125 − 0.2250 + 0
            = −0.3375  e·Å²

μ₂ · r_vec = (−0.067)(−0.5) + (0.033)(−1.0) + (−0.033)(4.5)
            = +0.0333 − 0.0333 − 0.1500
            = −0.1500  e·Å²
```

**Step 7e — plug into the energy formula:**

```
r³ = 21.50^(3/2) = 21.50 × 4.637 ≈  99.69  Å³
r⁵ = 21.50^(5/2) = 21.50² × 4.637 ≈ 2143.5  Å⁵

term1 =       −0.00758  /   99.69   =  −0.0000761  e²·Å⁻¹
term2 = 3 × (−0.3375)(−0.1500) / 2143.5
      = 3 × 0.050625 / 2143.5
      = 0.151875 / 2143.5
      = +0.0000709  e²·Å⁻¹

U = 14.3996 × (−0.0000761 − 0.0000709)
  = 14.3996 × (−0.0001470)
  ≈ −0.00212 eV    ←  ATTRACTIVE
```

**Why attractive?** Ti has +0.30 e and O has −0.20 e — opposite charges. Their
local dipoles point toward each other, making `μ₁ · μ₂` negative (term1 < 0).
Subtracting a positive term2 makes U even more negative.

---

### Pair B: sub_Si1 ↔ film_In1 — both positive charges → repulsive

```
r_vec = [0.5, 0.5, 4.0] − [0.0, 0.0, 0.0] = [0.5, 0.5, 4.0]
r     = √(0.25 + 0.25 + 16) = √16.5 ≈ 4.062 Å

μ₁ = μ_Si1 = [−0.300, −0.300, 0.000]  e·Å
μ₂ = μ_In1 = [−0.050, −0.050, −0.100] e·Å

μ₁ · μ₂  = (−0.3)(−0.05) + (−0.3)(−0.05) + (0)(−0.1) = +0.030

μ₁ · r_vec = (−0.3)(0.5) + (−0.3)(0.5) + (0)(4.0)    = −0.300
μ₂ · r_vec = (−0.05)(0.5) + (−0.05)(0.5) + (−0.1)(4.0) = −0.450

r³ = 16.5^(3/2) ≈ 67.07  Å³
r⁵ = 16.5^(5/2) ≈ 1106.7 Å⁵

term1 = 0.030 / 67.07 = +0.000447
term2 = 3 × (−0.300)(−0.450) / 1106.7 = 0.405 / 1106.7 = +0.000366

U = 14.3996 × (0.000447 − 0.000366)
  = 14.3996 × 0.000081
  ≈ +0.00117 eV    ←  REPULSIVE
```

**Why repulsive?** Both Si (+0.40 e) and In (+0.30 e) are positive. Their local
dipoles are similarly oriented so term1 is positive. The net energy is positive,
meaning the pair resists close contact.

---

## STEP 8 — `rank_interactions()` — building the final table

After computing all 12 pairs, you have a list of 12 result dicts. Each dict
contains the atom labels, charges, distance, local dipole magnitudes, and
interaction energy. `rank_interactions()` converts each dict into one row of a
pandas DataFrame, then sorts by `Interaction Energy (eV)` ascending (most
negative = most attractive → Rank 1). A 1-based `Rank` column is inserted at
the front.

**Conceptual view of the final table:**

| Rank | Substrate Atom | Film Atom | Distance (Å) | mu1 (e·Å) | mu2 (e·Å) | Energy (eV) | Type       |
|------|---------------|-----------|-------------|-----------|-----------|------------|------------|
| 1    | sub_Ti1       | film_O3   | 4.637       | 0.318     | 0.079     | −0.00212   | attractive |
| 2    | sub_O1        | film_In1  | 4.153       | 0.212     | 0.122     | −0.00150   | attractive |
| ...  | ...           | ...       | ...         | ...       | ...       | ...        | ...        |
| 11   | sub_Si1       | film_In1  | 4.062       | 0.424     | 0.122     | +0.00117   | repulsive  |
| 12   | sub_Ti1       | film_In1  | 3.536       | 0.318     | 0.122     | +0.00302   | repulsive  |

**What you can read from the table:**

- **Rank 1** identifies the substrate–film atom pair that has the strongest
  attractive interaction — the physically preferred bonding site.
- The **Distance** column is the raw 3D atom-to-atom separation r. Larger r
  means smaller energy magnitude because the formula falls as 1/r³.
- **mu1** and **mu2** are the *magnitudes* of the local dipoles
  (|qᵢ(rᵢ − r_centroid)|), not the whole-group dipoles. Bigger local dipole +
  smaller distance = stronger interaction.
- Opposite-charge pairs (Ti ↔ O, Si ↔ O) dominate the attractive end;
  same-sign pairs (Si ↔ In, Ti ↔ In) sit at the repulsive end.

---

## Summary — what does each quantity mean physically?

| Quantity                         | Physical meaning                                                                                          |
|----------------------------------|-----------------------------------------------------------------------------------------------------------|
| `calculate_dipole(atoms)`        | Overall polarity of the whole layer — how much and in which direction the layer's charge is "lopsided"    |
| `calculate_centroid(atoms)`      | Geometric centre of the layer — used as the "origin" when computing per-atom local dipoles                |
| `atomic_local_dipole(atom, c)`   | How much a single atom contributes to the layer's polarity, based on its charge and position within the layer |
| `r_vec` in energy formula        | Actual 3D vector from one atom to another — both direction and magnitude matter in dipole–dipole physics  |
| `r` (scalar distance)            | The inter-atomic separation used in the 1/r³ and 1/r⁵ denominators of the energy formula                 |
| `dipole_dipole_energy(μ₁,μ₂,r)` | Classical electrostatics: how strongly two local dipoles attract or repel, falls off as 1/r³              |
| `rank_interactions()` table      | Sorted leaderboard — Rank 1 is the substrate–film atom pair that most wants to sit next to each other     |

> **Key rule:** The `r` used in the energy formula is always the **direct
> atom-to-atom distance**, not anything centroid-related. The centroid only
> enters to compute the local dipole vectors μ₁ and μ₂.
