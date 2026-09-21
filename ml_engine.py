
# ============================================================
# 🌾 PESTRISK AI — PRODUCTION ML ENGINE
# ============================================================

import json
from pathlib import Path

import joblib
import pandas as pd


# ------------------------------------------------------------
# PATHS
# ------------------------------------------------------------

APP_DIR = Path(__file__).resolve().parent

CONFIG_PATH = APP_DIR / "artifact_config.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

MODEL_PATH = APP_DIR / CONFIG["ml_artifacts"]["model"]

FEATURE_PATH = APP_DIR / CONFIG["ml_artifacts"]["features"]

THRESHOLD_PATH = APP_DIR / CONFIG["ml_artifacts"]["thresholds"]


# ------------------------------------------------------------
# CACHED ARTIFACTS
# ------------------------------------------------------------

_model = None
_feature_data = None
_threshold_data = None


# ------------------------------------------------------------
# LOAD ARTIFACTS
# ------------------------------------------------------------

def load_artifacts():

    global _model
    global _feature_data
    global _threshold_data

    if _model is None:
        _model = joblib.load(MODEL_PATH)

    if _feature_data is None:
        with open(
            FEATURE_PATH,
            "r",
            encoding="utf-8"
        ) as f:
            _feature_data = json.load(f)

    if _threshold_data is None:
        with open(
            THRESHOLD_PATH,
            "r",
            encoding="utf-8"
        ) as f:
            _threshold_data = json.load(f)

    return (
        _model,
        _feature_data,
        _threshold_data
    )


# ------------------------------------------------------------
# FEATURE LIST
# ------------------------------------------------------------

def get_feature_list():

    _, feature_data, _ = load_artifacts()

    if isinstance(feature_data, list):
        return feature_data

    if isinstance(feature_data, dict):

        for key in [
            "features",
            "feature_list",
            "selected_features"
        ]:

            value = feature_data.get(key)

            if isinstance(value, list):
                return value

    raise ValueError(
        "Unable to determine feature list "
        "from feature_list.json"
    )


# ------------------------------------------------------------
# RISK THRESHOLDS
# ------------------------------------------------------------

def get_thresholds():

    _, _, threshold_data = load_artifacts()

    low = float(
        threshold_data.get(
            "low_threshold",
            0.50
        )
    )

    high = float(
        threshold_data.get(
            "high_threshold",
            0.70
        )
    )

    return low, high


# ------------------------------------------------------------
# RISK LABEL
# ------------------------------------------------------------

def probability_to_risk(probability):

    low, high = get_thresholds()

    if probability < low:
        return "Low"

    if probability < high:
        return "Medium"

    return "High"


# ------------------------------------------------------------
# PREDICTION
# ------------------------------------------------------------

def predict_risk(
    standard_week,
    max_temp,
    min_temp,
    rh1,
    rh2,
    rainfall,
    wind_speed,
    sunshine,
    evaporation,
    pest_name,
    location
):

    model, _, _ = load_artifacts()

    features = get_feature_list()

    row = {
        "Standard Week": standard_week,
        "MaxT": max_temp,
        "MinT": min_temp,
        "RH1(%)": rh1,
        "RH2(%)": rh2,
        "RF(mm)": rainfall,
        "WS(kmph)": wind_speed,
        "SSH(hrs)": sunshine,
        "EVP(mm)": evaporation,
        "PEST NAME": pest_name,
        "Location": location,
    }

    # Ensure exact production feature order
    X = pd.DataFrame(
        [[row.get(feature) for feature in features]],
        columns=features
    )

    # Calibrated probability of positive class
    probability = float(
        model.predict_proba(X)[0, 1]
    )

    risk_level = probability_to_risk(
        probability
    )

    return {
        "pest": pest_name,
        "location": location,
        "predicted_observation_risk": probability,
        "risk_level": risk_level,
        "interpretation": (
            f"The model predicts a {risk_level.lower()} "
            f"observation risk for {pest_name} "
            f"(probability {probability:.6f}). "
            "This is a predicted observation risk and "
            "does not by itself confirm infestation."
        )
    }


# ------------------------------------------------------------
# MODEL INFORMATION
# ------------------------------------------------------------

def get_model_info():

    model, _, thresholds = load_artifacts()

    return {
        "model_type": type(model).__name__,
        "feature_list": get_feature_list(),
        "thresholds": thresholds,
        "model_path": str(MODEL_PATH),
    }


# ------------------------------------------------------------
# MODULE TEST
# ------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 70)
    print("🌾 PESTRISK AI — ML ENGINE TEST")
    print("=" * 70)

    info = get_model_info()

    print("\nModel:")
    print(info["model_type"])

    print("\nFeatures:")
    for feature in info["feature_list"]:
        print("  •", feature)

    print("\nThresholds:")
    print(info["thresholds"])

    result = predict_risk(
        standard_week=30,
        max_temp=32,
        min_temp=25,
        rh1=80,
        rh2=75,
        rainfall=10,
        wind_speed=8,
        sunshine=6,
        evaporation=4,
        pest_name="Brown planthopper",
        location="Alappuzha"
    )

    print("\nPrediction:")
    print(json.dumps(
        result,
        indent=2
    ))

    print("\n" + "=" * 70)
    print("✅ ML ENGINE TEST COMPLETE")
    print("=" * 70)
