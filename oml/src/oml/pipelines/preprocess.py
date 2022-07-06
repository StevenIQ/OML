import csv
import requests
import pandas as pd
import datetime

from typing import Dict, Any

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from kedro.pipeline import Pipeline, node

from .nodes import encode_features, split_dataset



test_ratio: 0.3


def split_dataset(dataset: pd.DataFrame, test_ratio: float) -> Dict[str, Any]:
    """
    Splits dataset into a training set and a test set.
    """
    X = dataset.drop("purchased", axis=1)
    y = dataset["purchased"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_ratio, random_state=40
    )

    return dict(X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test)


def encode_features(dataset: pd.DataFrame) -> pd.DataFrame:
    """
    Encode features of data file.
    """
    features = dataset.drop(["user_id", "user_session"], axis=1).copy()

    encoders = []
    for label in ["category", "sub_category", "brand"]:
        features[label] = features[label].astype(str)
        features.loc[features[label] == "nan", label] = "unknown"
        encoder = LabelEncoder()
        features.loc[:, label] = encoder.fit_transform(features.loc[:, label].copy())
        encoders.append((label, encoder))

    features["weekday"] = features["weekday"].astype(int)
    return dict(features=features, transform_pipeline=encoders)





def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                encode_features,
                "primary",
                dict(features="dataset", transform_pipeline="transform_pipeline")
            ),
            node(
                split_dataset,
                ["dataset", "params:test_ratio"],
                dict(
                    X_train="X_train",
                    y_train="y_train",
                    X_test="X_test",
                    y_test="y_test"
                )
            )
        ]
    )



@hook_impl
def register_pipelines(self) -> Dict[str, Pipeline]:
    """Register the project's pipeline.

    Returns:
        A mapping from a pipeline name to a ``Pipeline`` object.

    """
    p_processing = processing_pipeline.create_pipeline()

    return {"processing": p_processing}