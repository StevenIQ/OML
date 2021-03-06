import numpy as np
import pandas as pd

from typing import Callable, Tuple, Any, Dict


from sklearn.base import BaseEstimator
from sklearn.metrics import mean_squared_error as MSE
from sklearn.model_selection import RepeatedKFold
from xgboost import XGBRegressor
from hyperopt import hp, tpe, fmin

import warnings
warnings.filterwarnings('ignore')

MODELS = [
    {
        "name": "xgboost",
        "class": XGBRegressor,
        "params": {
            'n_estimators': hp.quniform('n_estimators', 100, 1000, 1),
            'eta': hp.quniform('eta', 0.025, 0.5, 0.025),
            # A problem with max_depth casted to float instead of int with
            # the hp.quniform method.
            'max_depth':3,
            'min_child_weight': hp.quniform('min_child_weight', 1, 6, 1),
            'subsample': hp.quniform('subsample', 0.5, 1, 0.05),
            'gamma': hp.quniform('gamma', 0.5, 1, 0.05),
            'colsample_bytree': hp.quniform('colsample_bytree', 0.5, 1, 0.05),
            # 'eval_metric': 'auc',
            'objective': 'survival:cox',
            # Increase this number if you have more cores. Otherwise, remove it and it will default
            # to the maxium number.
            'nthread': 4,
            'booster': 'gbtree',
            'tree_method': 'exact',
            # "objective": "binary",
            # "verbose": 0,
            # # 'enable_categorical':"True",
            # 'eta':  0.002,
            # "max_depth": 3,
            # "objective": "survival:cox",
            # "subsample": 0.5
            # # "learning_rate": hp.uniform("learning_rate", 0.001, 1),
            # # "num_iterations": hp.quniform("num_iterations", 100, 1000, 20),
            # # "max_depth": hp.quniform("max_depth", 4, 12, 6),
            # # "num_leaves": hp.quniform("num_leaves", 8, 128, 10),
            # # "colsample_bytree": hp.uniform("colsample_bytree", 0.3, 1),
            # # "subsample": hp.uniform("subsample", 0.5, 1),
            # # "min_child_samples": hp.quniform("min_child_samples", 1, 20, 10),
            # # "reg_alpha": hp.choice("reg_alpha", [0, 1e-1, 1, 2, 5, 10]),
            # # "reg_lambda": hp.choice("reg_lambda", [0, 1e-1, 1, 2, 5, 10]),
        },
        "override_schemas": {
            "max_depth": int,
            "n_estimators": int,
        },
    }
]

def train_model(
    instance: BaseEstimator,
    training_set: Tuple[np.ndarray, np.ndarray],
    params: Dict = {},
) -> BaseEstimator:
    """
    Trains a new instance of model with supplied training set and hyper-parameters.
    """
    override_schemas = list(filter(lambda x: x["class"] == instance, MODELS))[0][
        "override_schemas"
    ]
    for p in params:
        if p in override_schemas:
            params[p] = override_schemas[p](params[p])
    model = instance(**params)
    model.fit(*training_set)
    return model

def optimize_hyp(
    instance: BaseEstimator,
    dataset: Tuple[np.ndarray, np.ndarray],
    search_space: Dict,
    metric: Callable[[Any, Any], float],
    max_evals: int = 40,
) -> BaseEstimator:
    """
    Trains model's instances on hyper-parameters search space and returns most accurate
    hyper-parameters based on eval set.
    """
    X, y = dataset

    def objective(params):
        rep_kfold = RepeatedKFold(n_splits=4, n_repeats=1)
        scores_test = []
        for train_I, test_I in rep_kfold.split(X):
            X_fold_train = X.iloc[train_I, :]
            y_fold_train = y.iloc[train_I].values.flatten()
            X_fold_test = X.iloc[test_I, :]
            y_fold_test = y.iloc[test_I].values.flatten()
            # On entra??ne une instance du mod??le avec les param??tres params
            model = train_model(
                instance=instance,
                training_set=(X_fold_train, y_fold_train),
                params=params
            )
            # On calcule le score du mod??le sur le test
            scores_test.append(
                metric(y_fold_test, model.predict(X_fold_test))
            )

        return np.mean(scores_test)

    return fmin(fn=objective, space=search_space, algo=tpe.suggest, max_evals=max_evals)

def auto_ml(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    max_evals: int = 40
) -> BaseEstimator:
    """
    Runs training of multiple model instances and select the most accurated based on objective function.
    """
    X = pd.concat((X_train, X_test))
    y = pd.concat((y_train, y_test))

    opt_models = []
    for model_specs in MODELS:
        # Finding best hyper-parameters with bayesian optimization
        optimum_params = optimize_hyp(
            model_specs["class"],
            dataset=(X, y),
            search_space=model_specs["params"],
            metric=lambda x, y: -MSE(x, y),
            max_evals=max_evals
        )
        print("done")
        # Training the supposed best model with found hyper-parameters
        model = train_model(
            model_specs["class"],
            training_set=(X_train, y_train),
            params=optimum_params,
        )
        opt_models.append(
            {
                "model": model,
                "name": model_specs["name"],
                "params": optimum_params,
                "score": MSE(y_test, model.predict(X_test)),
            }
        )

    # In case we have multiple models
    best_model = max(opt_models, key=lambda x: x["score"])
    return dict(model=best_model)