import joblib
import pandas as pd
import logging

from feature_extractor import extract_features

class DetectionModel:
    def __init__(self, model_path, name="default_engine", label_encoder=None):
        self.name = name

        try:
            self.model = joblib.load(f'./models/{model_path}')
        except Exception as e:
            raise

    def detect(self, flat_sample):
        features = extract_features(flat_sample)
        if features is None:
            logging.warning(f"Feature extraction failed. Sample: {flat_sample}")
            return None

        df = pd.DataFrame([features])
        df = df[self.model.feature_names_in_]

        try:
            prediction = self.model.predict(df)[0]
        except Exception as e:
            logging.exception("Error during prediction")
            return None

        if hasattr(self.model, "predict_proba"):
            confidence = float(self.model.predict_proba(df)[0].max())
        else:
            logging.warning("predict_proba exists but failed during execution")
            confidence = 1.0  # fallback

        return {
            "label": int(prediction),
            "confidence": round(confidence, 3)
        }
