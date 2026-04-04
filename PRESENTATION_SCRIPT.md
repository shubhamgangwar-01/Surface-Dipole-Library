# Surface Dipole Library — Presenter's Script

> **File:** `Surface_Dipole_Library_v2.pptx`
> **Duration:** ~25–30 minutes
> **Audience:** Professor / academic panel
>
> Instructions: Each slide section starts with `[SLIDE X]`. Text in
> `[brackets]` are stage directions — do not read aloud. Speak naturally;
> do not read word-for-word if possible. Key terms are **bold**.

---

## [SLIDE 1] — Title

*[Wait for the slide to appear, pause 2 seconds, then begin.]*

Good morning / Good afternoon, Professor.

Today I am presenting a Python library I have built called the
**Surface Dipole Library**. The full name describes exactly what it does:
it calculates **dipole moments** and **dipole-dipole interaction energies**
between the surface atoms of a glass substrate and a thin film.

The purpose of this library is to act as a **fast pre-screening tool**
before expensive computational simulations — specifically DFT, which stands
for Density Functional Theory.

As you can see on the right, the library consists of **8 Python modules**,
operates in **5 clearly defined processing steps**, evaluates up to **132
atom pairs** per test, and comes with **4 glass variants** built in.

I will walk you through everything — from the physics behind it, to the
code architecture, to two real test cases we ran on this library.

*[Click to next slide.]*

---

## [SLIDE 2] — Why This Library?

Let me start by explaining the problem this library is solving.

When you are researching which **thin-film material** to deposit on a
**glass substrate** — say, for a solar cell or a display — you typically
have 10 to 20 candidate materials. To truly understand how each material
will bond to the glass, you need a **DFT simulation**.

The problem is that a single DFT run takes anywhere from **hours to days**
of high-performance computing time, and costs hundreds to thousands of
dollars in cloud compute resources. If you have 20 candidates, you cannot
afford to run DFT on all 20.

*[Point to the Problem → Solution → Outcome flow diagram.]*

This library solves that problem. Instead of doing 20 DFT simulations, you
use the **surface_dipole_library** to compute dipole-dipole interaction
energies from **force-field partial charges** in under one second. You get
a ranked table of all candidates. Then you send only the **top 2 or 3** to
DFT.

This reduces your compute cost by approximately **90 percent**.

The four use cases at the bottom show where this is directly applicable —
**solar cells**, **display glass**, **optical coatings**, and academic
research. In all of these, ITO or TiO₂ or ZnO is deposited on glass, and
the interface quality determines device performance.

*[Click to next slide.]*

---

## [SLIDE 3] — Library Architecture

Now let me show you how the library is structured internally.

*[Point to the module grid.]*

The library is divided into **8 Python modules**, each handling exactly one
responsibility. This is a clean software engineering principle — separation
of concerns — which makes each module independently testable and
replaceable.

Let me walk through them briefly from top-left to bottom-right:

- **atoms.py** — defines the core data unit: the `Atom` dataclass. Every
  atom in the system is represented as an object with four fields: element,
  charge, position, and label.

- **io.py** — the input layer. It reads atom data from any file format:
  custom XYZ files, CIF crystal files, POSCAR files from VASP, or directly
  from ASE, which is the Atomic Simulation Environment library.

- **glass_substrate.py** — this is new in version 1.0. It stores the
  complete borosilicate glass surface definition inside the library itself.
  The user never needs to define the substrate manually.

- **geometry.py** — pure mathematical helpers: distance between atoms,
  displacement vectors, unit vectors, cutoff checking.

- **dipole.py** — implements the dipole moment formula μ = Σ qᵢrᵢ.

- **interaction.py** — implements the dipole-dipole energy formula. This
  is the core physics of the library.

- **ranking.py** — takes all the computed pair energies, sorts them, and
  returns a ranked pandas DataFrame.

- **main.py** — the high-level API. This is the single function the user
  calls: `analyze_film_on_glass`. It orchestrates all the other modules.

The flow goes from left to right: **Input → Dipole → Interaction → Ranked
Output**. At the bottom you can see the single import line a user needs.

*[Click to next slide.]*

---

## [SLIDE 4] — Input Modules

*[Point to atoms.py section.]*

Let me explain the three input-side modules in more detail.

**atoms.py** defines what an Atom object looks like. You can see on the
left: the user provides a Python dictionary with the element symbol, the
partial charge in units of the elementary charge e, and the xyz position in
Angstroms. The library converts this into a proper `Atom` object with
validation and auto-labelling.

*[Point to io.py section.]*

**io.py** handles four different input formats. If you have a crystal
structure file from an experiment — say a CIF file from the Cambridge
Structural Database — you load it with `load_from_ase`. If you have a
POSCAR output from a VASP DFT simulation, you use `load_from_poscar`. Or
if you are defining atoms manually in Python, you simply pass a list of
dictionaries directly.

*[Point to glass_substrate.py section.]*

**glass_substrate.py** is the most important new addition to this library.
The glass surface is stored directly inside the library — the user never
needs to define it.

*[Point to the layer diagram.]*

The borosilicate glass surface is modelled as **three distinct layers**:

- At z = 0 Å, the **silicon and boron backbone** atoms with positive charges.
- At z = 0.80 Å, the **bridging oxygens** — these connect two silicon
  tetrahedra and carry a moderate negative charge of −0.155 e.
- At z = 1.60 Å, the **non-bridging oxygens**, or NBO. These are the most
  negative atoms on the glass surface, at −0.290 e, and they are the
  **primary docking site** for film atoms.
- At z = 2.35 Å, the **silanol hydrogen** — this comes from surface
  hydroxylation when the glass is exposed to air moisture.

All charges come from the **ClayFF force field**, which was published by
Cygan, Liang and Kalinichev in the Journal of Physical Chemistry B in 2004.
This is the standard reference model for oxide surfaces in the materials
science community.

At the bottom you can see the four glass variants. **Borosilicate** is the
default — this represents commercial display glass, solar glass, and optical
glass. We also have fused silica (pure SiO₂), aluminosilicate (like Gorilla
Glass), and soda-lime (window glass).

*[Click to next slide.]*

---

## [SLIDE 5] — dipole.py — Formula μ = Σ qᵢrᵢ

Now let me get into the physics. The first formula the library uses is the
**electric dipole moment**.

*[Point to the orange WHY box.]*

Why do we care about the dipole moment? Because the dipole moment tells us
how **asymmetric** the charge distribution is in a group of atoms. A large
dipole moment means there is a strong local electric field. When two
surfaces face each other, the interaction between their dipoles determines
how strongly they will bond.

*[Point to the large navy formula box.]*

The formula is:

**μ equals the sum over all atoms of charge qᵢ times position rᵢ**

This is a vector sum. We multiply each atom's partial charge by its
3-dimensional position, and sum across all atoms in the surface group.
The result is the **dipole moment vector** in units of e·Å, which can
also be expressed in Debye.

*[Point to the three term boxes.]*

μ is the dipole moment vector. qᵢ is the partial charge — not the full
formal oxidation state, but a fractional charge from the force field that
accounts for covalent bonding and electronic screening. And rᵢ is simply
the (x, y, z) position of the atom in Angstroms.

*[Point to the worked example.]*

Let me show you a quick numerical example. We have three atoms: silicon
with charge +0.310, a bridging oxygen at −0.155, and a non-bridging oxygen
at −0.290. When we sum q times r for each atom, we get the dipole vector,
and taking its magnitude gives us 0.852 e·Å, which is about 4.09 Debye.

**What does the library give us from this step?** A dictionary containing
the full dipole vector, its magnitude in e·Å and in Debye, the individual
x, y, z components, the net charge, and the atom count. This is computed
separately for the glass and for the film.

*[Click to next slide.]*

---

## [SLIDE 6] — geometry.py & interaction.py

*[Point to geometry.py section.]*

**geometry.py** is a support module — it provides the mathematical
primitives that other modules depend on.

`displacement_vector` gives you the vector from atom 1 to atom 2.
`distance` gives you the scalar distance in Angstroms.
`unit_vector` normalises a vector to length 1 — this is the r-hat
direction vector used in the energy formula.
`are_within_cutoff` is the filter — if two atoms are farther apart than
the user-specified cutoff, that pair is excluded from the calculation.

*[Point to the interaction.py formula.]*

Now the central formula of the entire library — the **dipole-dipole
interaction energy**:

**U equals Kₑ times open bracket mu-1 dot mu-2 over r-cubed, minus 3
times mu-1 dot r-hat times mu-2 dot r-hat over r-cubed, close bracket**

Let me break this down:

- **Kₑ** is the Coulomb prefactor. In our unit system — charges in units
  of e, distances in Angstroms, energies in electron-volts — Kₑ equals
  **14.3996 eV·Å per e²**. This comes directly from SI units.

- **μ₁ and μ₂** are the local atomic dipole vectors for the two atoms
  forming the pair. We compute these in Step 3.

- **r** is the distance between the two atoms.

- **r-hat** is the unit vector pointing from one atom to the other.

The formula has two terms. The first term, μ₁·μ₂ divided by r³, captures
the **head-to-tail alignment** of the dipoles. The second term, with the
factor of 3, accounts for the **geometric orientation** — whether the
dipoles are aligned along the line connecting them, or perpendicular to it.

*[Point to the green and red boxes.]*

The sign convention is critical:
- **U less than zero means attractive** — the two atoms are pulling each
  other together. This is what we want for good adhesion.
- **U greater than zero means repulsive** — the atoms are pushing each
  other apart.

*[Click to next slide.]*

---

## [SLIDE 7] — ranking.py & main.py

*[Point to ranking.py.]*

**ranking.py** is the output engine. Once all pair energies are computed,
this module takes the list of results, applies the cutoff filter, sorts by
energy from most negative to most positive, and returns a **pandas
DataFrame** with a 1-based rank column.

*[Point to the mini table.]*

You can see what the table looks like. Rank 1 is always the most attractive
pair — the one the library recommends as the primary bonding pathway. Each
row shows the substrate atom label, the film atom label, the distance in
Angstroms, the energy in electron-volts, and whether it is attractive or
repulsive.

*[Point to main.py section.]*

**main.py** is what the user actually calls. The single function
`analyze_film_on_glass` is the entry point. When the user calls this
function with their film atom list, the library automatically:

1. Loads the correct glass substrate variant
2. Converts all input into Atom objects
3. Computes dipole moments for both surfaces
4. Generates all atom pairs and computes the interaction energy for each
5. Sorts the results and prints a formatted summary

This five-step process is what the next five slides will explain in detail.

*[Click to next slide.]*

---

## [SLIDE 8] — Step 1: Define Input Atoms

We now go inside the library and walk through the five processing steps
one at a time.

**Step 1 is input preparation.** This is the user-facing step — what the
researcher actually types.

*[Point to the code box on the left.]*

The user defines a Python list of dictionaries. Each dictionary represents
one film atom and has exactly three required fields: the **element** symbol,
the **charge** in units of e, and the **position** as an [x, y, z] list in
Angstroms. An optional label field can also be included.

This is the only thing the user needs to provide. The substrate — the glass
— is already inside the library and loads automatically.

*[Point to the library process boxes on the right.]*

Internally, the library validates the list is not empty, then converts each
dictionary into a proper Atom object via `load_from_dict_list`. It then
calls `assign_labels` to give each atom a unique, human-readable identifier
like `In5c1_film` or `O_term2_film`. Finally, it produces a `List[Atom]`
that is passed to Step 2.

*[Point to the Key Rules box.]*

One important rule for positioning: the glass surface occupies z = 0 to
z = 2.35 Angstroms. Film atom positions must have z-coordinates of at
least 3 Angstroms, and typically between 3.5 and 5.5 Angstroms for a
realistic surface layer.

*[Point to the How to Get Charges box.]*

For partial charges, there are four standard approaches: published force
field tables — ClayFF for oxides, Matsui-Akaogi for TiO₂, and so on. Bader
charge analysis from a DFT run. The pymatgen bond valence analyser. Or
simply using values from the literature that have been validated
experimentally.

*[Click to next slide.]*

---

## [SLIDE 9] — Step 2: Calculate Dipole Moments

**Step 2 applies the dipole moment formula** to both the glass surface and
the film separately.

*[Point to the formula.]*

We use the formula we just discussed: μ equals the sum of qᵢ times rᵢ.

*[Point to the two result boxes.]*

For the **glass substrate** — which has 12 atoms — the library computes a
dipole vector of roughly [−0.62, −0.20, −1.48] in e·Å, with a magnitude of
**1.613 e·Å, or 7.748 Debye**. The net charge of the glass surface is
slightly negative at −0.115 e.

For the **ITO film** — 11 atoms — the dipole is [−0.75, −0.03, −2.84]
e·Å, with a magnitude of **2.934 e·Å, or 14.09 Debye**. The net charge is
slightly positive at +0.170 e.

*[Point to the green insight box.]*

This is already telling us something important before we even calculate
pair energies. The ITO film has a **significantly larger dipole moment**
than the glass — nearly twice as large. And the net charges are opposite in
sign — ITO is slightly positive, glass is slightly negative. These two
surfaces are **electrostatically complementary**. They will naturally attract
each other.

*[Point to the worked example.]*

At the bottom I show a quick two-atom worked example so you can see how the
summation actually works numerically. Atom 1 has charge +0.78 at position
z = 3.5 Å. Atom 2 has charge −0.52 at position z = 4.9 Å. We multiply
and sum, and we get a z-component of +0.18 e·Å for this two-atom fragment.

*[Click to next slide.]*

---

## [SLIDE 10] — Step 3: Geometric Centroids & Local Atomic Dipoles

**Step 3 introduces the concept of the local atomic dipole.** This is
perhaps the most subtle step in the calculation, so let me explain it
carefully.

*[Point to the centroid formula.]*

First, for each group of atoms — glass and film separately — we compute the
**geometric centroid**. This is simply the arithmetic average of all atomic
positions: sum the positions, divide by N. It gives us the geometric centre
of mass of the surface group.

*[Point to the local dipole formula.]*

Then, for each individual atom, we compute its **local dipole vector**:
μᵢ equals qᵢ times the quantity rᵢ minus the centroid.

What this means is: instead of measuring an atom's position from the
absolute coordinate origin, we measure it **relative to the centre of its
own surface group**.

*[Point to the WHY box.]*

Why do we do this? Because the dipole-dipole formula needs the dipole of
each individual atom as if it were the centre of its group. Using the
centroid as the reference removes any artificial offset from the coordinate
system. No matter where the glass surface is placed in space, the local
dipoles will be the same.

*[Point to the schematic on the left.]*

Here you can see the glass atoms scattered in 3D space. The centroid is
computed as their geometric average. Then for each atom — here I show
O_NBO1 as an example — we subtract the centroid position from the atom's
position, multiply by the charge, and get the local dipole vector
[+0.734, +0.424, −0.194] e·Å.

This local dipole vector is what gets substituted into the energy formula
as μ₁ or μ₂ in Step 4.

*[Click to next slide.]*

---

## [SLIDE 11] — Step 4: Pairwise Dipole-Dipole Interaction Energy

**Step 4 is the core calculation.** This is where we compute the actual
interaction energy between every pair of atoms — one from the glass surface,
one from the film.

*[Point to the full formula.]*

The formula, once more:

U equals Kₑ times open bracket mu-1 dot mu-2 over r-cubed, minus 3 times
mu-1 dot r-hat times mu-2 dot r-hat over r-cubed, close bracket.

Kₑ is 14.3996 eV·Å per e². μ₁ and μ₂ are the local dipole vectors from
Step 3. r is the distance. r-hat is the unit vector.

*[Point to the worked example section.]*

Let me walk through the actual numbers for the best pair in our ITO test.

The glass atom is **O_NBO1** — a non-bridging oxygen at position
[0, 0, 1.60] Å with charge −0.290 e.

The film atom is **In5c1** — a surface indium atom at position
[0, 0, 3.50] Å with charge +0.780 e.

The displacement vector r is [0, 0, 3.50] minus [0, 0, 1.60], which gives
[0, 0, 1.90] Å. The distance is **1.90 Angstroms**.

*[Point to the local dipoles.]*

Using the centroid values computed in Step 3:
- The local dipole of O_NBO1 is [+0.734, +0.424, −0.194] e·Å
- The local dipole of In5c1 is [0, 0, +1.872] e·Å

*[Point to the green result box.]*

Plugging these into the formula:

U equals 14.3996 times open bracket the dot products divided by 1.90 cubed,
minus 3 times the r-hat projections close bracket...

and the result is **−3.4416 electron-volts**.

*[Point to the bottom navy box.]*

This is strongly attractive. −3.44 eV is a large number for a
dipole-dipole interaction. It tells us that the O_NBO site on the glass
surface and the In5c site on the ITO film have an exceptionally strong
electrostatic attraction. This is the **primary bonding pathway** between
these two materials.

*[Click to next slide.]*

---

## [SLIDE 12] — Step 5: Rank All Pairs → Output Table

**Step 5 assembles everything into the final output.**

*[Point to the four flow boxes at the top.]*

After computing the energy for every possible atom pair, the library:
1. Takes all N×M pairs — where N is the number of glass atoms and M is
   the number of film atoms.
2. Applies the cutoff filter — removing any pair farther apart than the
   specified cutoff distance.
3. Sorts all remaining pairs by energy in ascending order — most negative
   first.
4. Returns a **pandas DataFrame** with a 1-based rank column.

For our test — 12 glass atoms times 11 ITO film atoms — that gives us
**132 pairs**.

*[Point to the ranked table.]*

Here is a portion of the actual output table. Rank 1 is O_NBO1_sub
interacting with In5c1_film at −3.44 eV, distance 1.90 Å — strongly
attractive. Rank 2 is the silanol hydrogen with In5c1 at −0.95 eV. And
so on down to Rank 132, which is O_NBO1 with Sn_dp1 at +0.48 eV —
repulsive.

*[Point to the blue result dict box.]*

The library also exposes a `best_interaction` dictionary directly — no need
to index into the DataFrame. It gives you the substrate atom name, film atom
name, energy in eV, distance in Angstroms, and the interaction type — all
in one clean dictionary.

This is the complete output of the five-step process. We now have a fully
ranked table of every glass-film atom interaction, and we know exactly
which pair is the strongest and which is the weakest.

*[Click to next slide.]*

---

## [SLIDE 13] — Test 1: TiO₂ Film on Borosilicate Glass

Now let me show you the two tests we ran on this library.

**Test 1 uses TiO₂ — titanium dioxide** — a rutile-phase thin film on
borosilicate glass. This is one of the most widely studied thin-film
systems in the world, used in solar cells, self-cleaning coatings, and
photocatalysts.

*[Point to the ITO atom table on the left.]*

The TiO₂ film surface has **11 atoms**. The most important are the Ti5c
atoms — 5-fold coordinated titanium atoms — which are the most reactive
sites on the rutile (110) surface. They carry a charge of +0.580 e,
derived from the **Matsui-Akaogi** force field. We also have bridging
oxygens, in-plane oxygens, and a surface hydroxyl group.

*[Point to the test results on the right.]*

We ran **6 unit tests** on this system. All 6 pass. The tests verify:
- That dipole moments are finite and non-negative
- That the interaction table has the correct structure and is properly sorted
- That the best interaction is indeed attractive — which it is
- That a specific known distance computes correctly
- That the cutoff filter reduces the pair count as expected
- That the energy formula is symmetric — U(μ₁,μ₂) equals U(μ₂,μ₁)

*[Point to the findings section.]*

The key finding is that **Rank 1 is O_NBO1 interacting with Ti5c1 at
−2.22 eV** at a distance of 1.90 Angstroms. This is the Non-Bridging
Oxygen on the glass surface directly below the surface titanium atom.
The Rank 2 and 3 pairs involve the same O_NBO site at longer range, and
the silanol hydrogen.

*[Point to the green verdict bar.]*

**Verdict: TiO₂ is a good candidate for borosilicate glass.** The
electrostatic anchoring through O_NBO to Ti5c predicts strong adhesion,
which is consistent with decades of experimental literature.

*[Click to next slide.]*

---

## [SLIDE 14] — Test 2: ITO Film on Borosilicate Glass

**Test 2 uses ITO — Indium Tin Oxide.** This is the transparent conductive
oxide used as the front electrode in virtually every solar cell and flat
panel display in the world. ITO is In₂O₃ doped with approximately 10 mol%
SnO₂.

*[Point to the ITO atom table.]*

The ITO film surface has **11 atoms**: three surface indium atoms
(In5c, 5-fold coordinated), one tin dopant (Sn⁴⁺ substituting an In³⁺
site), four bridging oxygens, and three terminal oxygens.

The key charge values are: **In5c at +0.780 e** and **Sn dopant at
+0.950 e** — the highest charge in the film. These come from the Hamad,
Moreira and Catlow paper in the Journal of Physical Chemistry C, 2011.

*[Point to the 8 test results.]*

We ran **8 unit tests** — two more than the TiO₂ test — because this uses
the new glass-fixed API. All 8 pass.

The two additional tests are:
- `test_glass_variant_key_present` — verifies that the result dictionary
  includes the `glass_variant` and `glass_atoms` keys that are new in this
  API.
- `test_sn_has_attractive_interactions` — verifies that the Sn dopant
  produces at least one attractive interaction with the glass, confirming
  it contributes meaningfully to adhesion.

*[Point to the findings section.]*

The top finding: **O_NBO1 interacting with In5c1 at −3.44 eV**, distance
1.90 Å. This is 55% stronger than TiO₂'s best pair. The reason is that
indium carries a higher partial charge (+0.78 e) than titanium (+0.58 e),
giving it a larger local dipole moment.

Something interesting in Rank 2 and Rank 3: the **silanol hydrogen
H_OH1** appears. The silanol H at z = 2.35 Å is the closest glass atom
to the ITO layer — only 1.50 Å from In5c1. Even though H has only +0.175 e,
its proximity makes it the second-strongest attractor. This confirms
experimental observations that **UV-ozone or plasma pre-treatment of glass**
— which increases the silanol density — improves ITO film quality.

*[Point to the verdict bar.]*

**Verdict: ITO is an excellent candidate for borosilicate glass.** The
bonding is stronger, the film is electrostatically complementary, and
multiple anchor sites distribute the bonding load across the interface.

*[Click to next slide.]*

---

## [SLIDE 15] — Comparison: TiO₂ vs ITO

*[Point to the full comparison table.]*

This slide puts the two tests side by side so we can compare directly.

The same glass substrate was used for both. The same cutoff of 8 Angstroms.
The same 12 glass atoms. The only difference is the film.

Some key comparisons:

- **Primary cation charge**: TiO₂ has Ti at +0.58 e; ITO has In at +0.78 e.
  This difference in charge is the single most important factor in the
  energy difference.

- **Film dipole moment**: TiO₂ gives 10.05 Debye; ITO gives 14.09 Debye.
  ITO's dipole is 40% larger. A larger dipole means stronger interactions
  at the same distance.

- **Best energy**: TiO₂ gives −2.22 eV; ITO gives **−3.44 eV**. That is
  a 55% difference — meaning ITO bonds to glass almost 1.5 times more
  strongly than TiO₂ at the primary site.

- **Pair geometry**: Both have their best pair at exactly **1.90 Å** —
  because in both cases it is the vertically aligned O_NBO ↔ surface cation
  pair. The geometry is identical; the difference comes entirely from the
  charges.

- **Silanol H contribution**: In TiO₂ the silanol H appears at Rank 3; in
  ITO it appears at Rank 2. ITO's indium has a larger dipole, so H_OH is
  pulled in more strongly.

- Both systems scored **GOOD or EXCELLENT** verdicts. Neither is a bad
  candidate — but ITO is clearly superior from a purely electrostatic
  screening perspective.

*[Click to next slide.]*

---

## [SLIDE 16] — Conclusion

*[Point to the introductory text.]*

To summarise what this library does and what we demonstrated:

The surface_dipole_library reduces candidate screening from days to seconds
by computing dipole-dipole interaction energies from validated force-field
charges.

*[Point to the four conclusion cards.]*

**Card 1 — Physics-based ranking.** This library is not a lookup table. It
uses the classical dipole-dipole formula with 3-dimensional geometry and
actual atomic charges. The ranking reflects real electrostatic physics.

**Card 2 — Glass substrate built-in.** With the new glass-fixed API, the
user only defines the film. The substrate loads automatically, and all four
glass compositions are available.

**Card 3 — Test Results.** We tested two real materials: TiO₂ with a best
bond of −2.22 eV, and ITO with −3.44 eV. ITO wins — its higher-charge
indium and tin cations anchor more strongly to the glass non-bridging oxygens.

**Card 4 — What's next.** The natural next step is to take the top-ranked
candidates from this library and submit them to a full DFT simulation — for
example using VASP or Quantum ESPRESSO. The library narrows 20 candidates
down to 2 or 3, making that DFT budget manageable.

*[Point to the code snippet at the bottom.]*

And here is the simplicity of the user experience. Three lines of Python.
You get the full ranked table in under one second.

*[Pause briefly.]*

This library is production-ready, MIT-licensed, and fully documented with
a WALKTHROUGH, ATOM_LABELS guide, INPUT_GUIDE, and two TEST case study
documents. All code is on GitHub.

Thank you — I am happy to take any questions.

*[Click to final slide.]*

---

## [SLIDE 17] — References

*[Only show this slide if asked, or mention it briefly.]*

These are the nine references that underpin the scientific content of this
library.

The most important ones are:

- **[1] Cygan et al. 2004** — ClayFF force field. All glass partial charges
  come from this paper.

- **[2] Matsui & Akaogi 1991** — the TiO₂ partial charges for the test.

- **[3] Hamad, Moreira & Catlow 2011** — the ITO and In₂O₃ partial charges.

- **[6] Griffiths 2013** — the classical electrodynamics textbook for the
  dipole moment formula.

- **[7] Jackson 1999** — the classical electrodynamics textbook for the
  dipole-dipole energy formula.

Every slide in this presentation that uses external data — charges, formulas,
crystal structures — has a reference cited in the footer at the bottom.

---

## Quick Reference — Key Numbers

| Item | Value |
|------|-------|
| Glass atoms | 12 (borosilicate) |
| TiO₂ film atoms | 11 |
| ITO film atoms | 11 |
| Total pairs per test | 132 |
| TiO₂ best bond energy | −2.2235 eV |
| ITO best bond energy | −3.4416 eV |
| ITO improvement over TiO₂ | +55% stronger |
| Best pair (both) | O_NBO1_sub ↔ cation at 1.90 Å |
| Kₑ (Coulomb prefactor) | 14.3996 eV·Å/e² |
| 1 e·Å in Debye | 4.803 D |
| Glass dipole |μ| | 1.613 e·Å = 7.748 D |
| TiO₂ film dipole |μ| | 2.093 e·Å = 10.05 D |
| ITO film dipole |μ| | 2.934 e·Å = 14.09 D |
| Unit tests (TiO₂) | 6/6 PASS |
| Unit tests (ITO) | 8/8 PASS |

---

## Likely Questions & Answers

**Q: Why partial charges instead of formal oxidation states?**

A: Formal oxidation states like Si⁴⁺ (+4) or Ti⁴⁺ (+4) are integer values
that assume purely ionic bonding. Real oxides are partly covalent — electron
density is shared between the metal and oxygen. The ClayFF force field
derives partial charges by fitting to ab initio quantum mechanical
calculations, so they capture this covalent character. Using +4 for silicon
would dramatically overestimate the dipole moment and produce unrealistic
energies.

**Q: Is this model physically rigorous enough for real predictions?**

A: This library is a **pre-screening tool**, not a replacement for DFT. It
models electrostatic dipole-dipole interactions only — it does not include
polarizability (induction), van der Waals dispersion, or covalent bonding.
For a quick ranking of 10 to 20 candidates, it is fast and directionally
correct. The final quantitative answer still requires DFT, but the library
tells you which candidates are worth the compute budget.

**Q: Why does ITO have a stronger bond than TiO₂ if TiO₂ has a higher
formal charge (Ti⁴⁺) than In³⁺?**

A: Formal charges do not matter here — what matters is the **partial charge
from the force field**. In the force field, indium In is assigned +0.780 e
while titanium Ti5c is +0.580 e. So In carries more effective charge
than Ti in the FF model. Additionally, In has a larger local dipole moment
because its position and coordination give a larger (rᵢ − centroid) vector.
Both effects together make the O_NBO ↔ In5c interaction 55% stronger.

**Q: What does the cutoff parameter do?**

A: The cutoff parameter — default 8.0 Angstroms — filters out atom pairs
that are farther apart than this distance. Pairs beyond the cutoff are
excluded from the table. This both speeds up the calculation for large
supercells and also makes physical sense: dipole-dipole energy falls off
as 1/r³, so very distant pairs contribute negligibly.

**Q: Why are there 132 pairs specifically?**

A: 12 glass atoms multiplied by 11 film atoms equals 132. Every possible
combination of one glass atom with one film atom is evaluated. With a
cutoff of 8 Å, all 132 pairs survive for both TiO₂ and ITO because the
maximum glass-film distance in these test geometries is about 7.3 Å.

---

*End of Script*

*surface_dipole_library v1.0.0 — Presentation Script*
