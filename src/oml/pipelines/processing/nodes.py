import pandas as pd

from typing import Dict, Any

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

def encode_features(dataset: pd.DataFrame) -> pd.DataFrame:
    """
    Encode features of data file.
    """

    features = dataset.copy()

    encoders = []
    for label in ["sex_isFemale", "age", "physical_activity", "serum_albumin", "alkaline_phosphatase", "SGOT", "BUN",
                  "calcium", "creatinine", "potassium", "sodium", "total_bilirubin", "serum_protein", "red_blood_cells",
                  "white_blood_cells", "hemoglobin", "hematocrit", "segmented_neutrophils", "lymphocytes", "monocytes",
                  "eosinophils", "basophils", "band_neutrophils", "cholesterol", "sedimentation_rate", "uric_acid",
                  "systolic_blood_pressure", "pulse_pressure"]:
        features[label] = features[label].astype(str)
        features.loc[features[label] == "nan", label] = "unknown"
        encoder = LabelEncoder()
        features.loc[:, label] = encoder.fit_transform(features.loc[:, label].copy())
        encoders.append((label, encoder))
        if label == "sex_isFemale":
            features[label] = features[label].astype(bool)
    
    return dict(features=features, transform_pipeline=encoders)


def split_dataset(dataset: pd.DataFrame, test_ratio: float) -> Dict[str, Any]:
    """
    Splits dataset into a training set and a test set.
    """
    X = dataset.drop(["y", "date"], axis=1).copy()
    y = dataset[["y"]]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_ratio, random_state=40
    )

    return dict(X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test)