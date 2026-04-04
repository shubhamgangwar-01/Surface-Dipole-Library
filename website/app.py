"""
app.py
------
Flask web application for the surface_dipole_library documentation and
interactive interface tool.

Routes:
    GET  /                → Landing page
    GET  /docs            → Documentation page
    GET  /case-studies    → Case studies (TiO2 and ITO)
    GET  /tool            → Interactive analysis tool
    POST /api/analyze     → JSON API for film-on-glass analysis
"""

import sys
import os

# Ensure the library one level up is importable when running from this directory
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Page routes
# ---------------------------------------------------------------------------


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/docs")
def docs():
    return render_template("docs.html")


@app.route("/case-studies")
def case_studies():
    return render_template("case_studies.html")


@app.route("/tool")
def tool():
    return render_template("tool.html")


# ---------------------------------------------------------------------------
# API endpoint
# ---------------------------------------------------------------------------


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """
    POST /api/analyze

    Request JSON:
    {
        "film_atoms": [
            {
                "element": "Ti",
                "charge": 0.58,
                "position": [0.0, 0.0, 3.5],
                "label": "Ti5c1_film"
            },
            ...
        ],
        "cutoff": 8.0,
        "glass_variant": "borosilicate"
    }

    Response JSON:
    {
        "glass_variant": "borosilicate",
        "n_pairs": 132,
        "n_atoms_film": 11,
        "substrate_dipole": {
            "magnitude": 1.613,
            "debye": 7.75,
            "mu_x": -0.6184,
            "mu_y": -0.1971,
            "mu_z": -1.4768,
            "total_charge": -0.115
        },
        "film_dipole": { ... },
        "best": {
            "substrate_atom": "O_NBO1_sub",
            "film_atom": "Ti5c1_film",
            "energy_eV": -2.2243,
            "distance_ang": 1.90,
            "interaction_type": "attractive",
            "substrate_charge": -0.290,
            "film_charge": 0.580
        },
        "pairs": [ ... ],
        "stats": {
            "attractive": 67,
            "repulsive": 65,
            "neutral": 0
        },
        "error": null
    }
    """
    try:
        data = request.get_json(force=True)

        film_atoms_raw = data.get("film_atoms", [])
        cutoff = float(data.get("cutoff", 8.0))
        glass_variant = str(data.get("glass_variant", "borosilicate"))

        if not film_atoms_raw:
            return jsonify({"error": "film_atoms list is empty."}), 400

        # Build atom dict list expected by the library
        film_atoms = []
        for atom in film_atoms_raw:
            entry = {
                "element":  str(atom["element"]),
                "charge":   float(atom["charge"]),
                "position": [
                    float(atom["position"][0]),
                    float(atom["position"][1]),
                    float(atom["position"][2]),
                ],
            }
            if "label" in atom and atom["label"]:
                entry["label"] = str(atom["label"])
            film_atoms.append(entry)

        from surface_dipole_library import analyze_film_on_glass

        result = analyze_film_on_glass(
            film_atoms=film_atoms,
            cutoff=cutoff,
            glass_variant=glass_variant,
            verbose=False,
        )

        # ── Dipole moment helpers ──────────────────────────────────────────
        def _dipole_dict(d):
            return {
                "magnitude":    round(float(d["dipole_magnitude"]), 6),
                "debye":        round(float(d["dipole_debye"]), 4),
                "mu_x":         round(float(d["mu_x"]), 6),
                "mu_y":         round(float(d["mu_y"]), 6),
                "mu_z":         round(float(d["mu_z"]), 6),
                "total_charge": round(float(d["total_charge"]), 6),
            }

        # ── Interaction table → list of dicts ─────────────────────────────
        df = result["interaction_table"]
        pairs = []
        for _, row in df.iterrows():
            pairs.append({
                "rank":             int(row["Rank"]),
                "substrate_atom":   str(row["Substrate Atom"]),
                "film_atom":        str(row["Film Atom"]),
                "substrate_element": str(row["Substrate Element"]),
                "film_element":     str(row["Film Element"]),
                "substrate_charge": round(float(row["Substrate Charge (e)"]), 4),
                "film_charge":      round(float(row["Film Charge (e)"]), 4),
                "distance_ang":     round(float(row["Distance (Å)"]), 4),
                "mu1_magnitude":    round(float(row["mu1 Magnitude (e·Å)"]), 6),
                "mu2_magnitude":    round(float(row["mu2 Magnitude (e·Å)"]), 6),
                "energy_eV":        round(float(row["Interaction Energy (eV)"]), 6),
                "interaction_type": str(row["Interaction Type"]),
            })

        # ── Statistics ────────────────────────────────────────────────────
        type_col = df["Interaction Type"]
        stats = {
            "attractive": int((type_col == "attractive").sum()),
            "repulsive":  int((type_col == "repulsive").sum()),
            "neutral":    int((type_col == "neutral").sum()),
        }

        # ── Best interaction ──────────────────────────────────────────────
        best = result["best_interaction"]
        best_out = {
            "substrate_atom":   str(best["substrate_atom"]),
            "film_atom":        str(best["film_atom"]),
            "energy_eV":        round(float(best["energy_eV"]), 6),
            "distance_ang":     round(float(best["distance_ang"]), 4),
            "interaction_type": str(best["interaction_type"]),
            "substrate_charge": round(float(best["substrate_charge"]), 4),
            "film_charge":      round(float(best["film_charge"]), 4),
        }

        return jsonify({
            "glass_variant":    glass_variant,
            "n_pairs":          int(result["n_pairs"]),
            "n_atoms_film":     len(film_atoms),
            "substrate_dipole": _dipole_dict(result["substrate_dipole"]),
            "film_dipole":      _dipole_dict(result["film_dipole"]),
            "best":             best_out,
            "pairs":            pairs,
            "stats":            stats,
            "error":            None,
        })

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, port=8080)
