import os
import mlflow
import joblib

from mlflow.tracking import MlflowClient

ENV = os.getenv("ENV")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/app/conf/key.json"

mlflow.set_tracking_uri(os.getenv("MLFLOW_SERVER"))

class Model():

    def __init__(self):
        self.model = None
        self.transform_pipeline = None
        self.load_model()

    def load_model(self):
        # We query currently staging or production model, according to environment specification
        client = MlflowClient()
        model_version = client.get_latest_versions(os.getenv("MLFLOW_REGISTRY_NAME"), [ENV])[0]
        pipeline_path = client.download_artifacts(model_version.run_id, "transform_pipeline.pkl")

        self.model = mlflow.sklearn.load_model("runs:/{}/model".format(model_version.run_id))
        # We must also retrieve transform pipeline from artifacts
        self.transform_pipeline = joblib.load(pipeline_path)

    def predict(self, X):
        # if self.model:
        #     if self.transform_pipeline:
        #         for name, encoder in self.transform_pipeline:
        #             X[name] = X[name].fillna("unknown")
        #             X[name] = encoder.transform(X[name])
        #     for col in ["user_id", "user_session", "purchased"]:
        #         if col in X:
        #             X = X.drop(col, axis=1)
        #     return self.model.predict(X)
        return None