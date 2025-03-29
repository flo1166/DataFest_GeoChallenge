import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
import logging
from typing import Tuple, List, Optional, Dict
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(config_path: str = "config.json") -> Dict:
    """
    Load and return configuration from a JSON file.
    """
    try:
        with open(config_path, "r") as file:
            config = json.load(file)
        return config
    except Exception as e:
        logging.error(f"Error loading configuration from {config_path}: {e}")
        raise

def preprocess_data(
    df: pd.DataFrame, 
    target: str, 
    numerical_cols: List[str], 
    categorical_cols: List[str], 
    grid_col: Optional[str] = None, 
    id_col: Optional[str] = None, 
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Preprocess the data by:
      - Splitting the grid cell column (if provided) into 'east' and 'north' columns.
      - One-hot encoding low-cardinality categorical variables.
      - Dropping the identifier column if provided.
      - Separating features and target.
    
    Parameters:
        df (pd.DataFrame): Input data.
        target (str): Name of the target variable.
        numerical_cols (list): List of numerical column names.
        categorical_cols (list): List of low-cardinality categorical column names.
        grid_col (str, optional): Name of the grid cell column (expected format "east_value_north_value").
        id_col (str, optional): Name of an identifier column to drop.
        handle_missing (str, optional): Strategy for handling missing values ('drop' or 'fill').
    
    Returns:
        X (pd.DataFrame): Preprocessed feature DataFrame.
        y (pd.Series): Target variable.
    """
    df = df.copy()

    # If a grid cell column is provided, split it into 'east' and 'north'
    if grid_col and grid_col in df.columns:
        # Expected format: "east_value_north_value"
        grid_split = df[grid_col].str.split('_', expand=True)
        df['east'] = pd.to_numeric(grid_split[0], errors='coerce')
        df['north'] = pd.to_numeric(grid_split[1], errors='coerce')
        # Optionally add these new features to the numerical columns list if not already included
        if 'east' not in numerical_cols:
            numerical_cols.append('east')
        if 'north' not in numerical_cols:
            numerical_cols.append('north')
        # Drop the original grid column
        df.drop(grid_col, axis=1, inplace=True)
    
    # One-hot encode low-cardinality categorical variables
    if categorical_cols:
        df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)
    
    # Drop the identifier column if provided
    if id_col and id_col in df.columns:
        df.drop(id_col, axis=1, inplace=True)
    
    # Separate target and features
    y = df[target]
    X = df.drop(target, axis=1)
    return X, y

def train_model(
    X: pd.DataFrame, 
    y: pd.Series, 
    test_size: float = 0.2, 
    random_state: int = 42, 
    params: Optional[Dict] = None, 
    num_boost_round: int = 1000, 
    early_stopping_rounds: int = 50, 
    seed: Optional[int] = None
) -> Tuple[lgb.Booster, Dict[str, float], pd.DataFrame]:
    """
    Train a LightGBM model on the provided data.
    
    Parameters:
        X (pd.DataFrame): Feature matrix.
        y (pd.Series): Target variable.
        test_size (float): Proportion of data for the validation set.
        random_state (int): Random seed for reproducibility.
        params (dict, optional): Parameters for LightGBM. Uses defaults if None.
        num_boost_round (int): Maximum number of boosting iterations.
        early_stopping_rounds (int): Rounds for early stopping.
        seed (int, optional): Random seed for reproducibility in LightGBM.
    
    Returns:
        model (lgb.Booster): The trained LightGBM model.
        metrics (dict): Dictionary containing RMSE and MAE.
        feature_importances (pd.DataFrame): DataFrame with feature importances.
    """
    # Set default LightGBM parameters if not provided
    if params is None:
        params = {
            'objective': 'regression',
            'metric': ['rmse', 'mae'],
            'boosting': 'gbdt',
            'learning_rate': 0.05,
            'verbose': -1,
            'n_jobs': -1,
            'seed': seed  # Add seed for reproducibility
        }
    
    # Split the data into training and validation sets
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    # Prepare LightGBM datasets
    train_data = lgb.Dataset(X_train, label=y_train)
    val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
    
    logging.info("Training the LightGBM model...")
    model = lgb.train(
        params,
        train_data,
        num_boost_round=num_boost_round,
        valid_sets=[train_data, val_data],
        early_stopping_rounds=early_stopping_rounds,
        verbose_eval=100
    )
    
    # Evaluate model performance
    y_pred = model.predict(X_val, num_iteration=model.best_iteration)
    rmse = np.sqrt(mean_squared_error(y_val, y_pred))
    mae = mean_absolute_error(y_val, y_pred)
    metrics = {'RMSE': rmse, 'MAE': mae}
    
    logging.info("Validation RMSE: {:.4f}".format(rmse))
    logging.info("Validation MAE: {:.4f}".format(mae))
    
    # Create a DataFrame for feature importances
    feature_importances = pd.DataFrame({
        'feature': X_train.columns,
        'importance': model.feature_importance()
    }).sort_values(by='importance', ascending=False)
    
    return model, metrics, feature_importances

