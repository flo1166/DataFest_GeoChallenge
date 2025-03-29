from data_modelling import preprocess_data, train_model, load_config
from data_cleaning import clean_data, display_years
import pandas as pd
import shap


# Load dataset
df = pd.read_csv('Data/HiDrive/panel/CampusFile_WM_cities.csv')


# Load configuration from config.json
config = load_config("config.json")
preproc_cfg = config["preprocess"]
training_cfg = config["training"]

# Clean the data using configuration parameters
columns_for_model = [preproc_cfg["target"]] + preproc_cfg["numerical_cols"] + preproc_cfg["categorical_cols"] + preproc_cfg["temporal_cols"] + preproc_cfg["spatial_cols"]
df = clean_data(df, columns_for_model)

# Change year cols
df_years = display_years(df)

# Export the cleaned DataFrame to a CSV file
df_years.to_csv("Data/HiDrive/panel/CampusFile_WM_cities_cleaned.csv", index=False)

# # Preprocess the data using configuration parameters
# X, y = preprocess_data(
#    df,
#    preproc_cfg["target"],
#    preproc_cfg["numerical_cols"],
#    preproc_cfg["categorical_cols"],
#    preproc_cfg.get("grid_col"),
#    preproc_cfg.get("id_col")
#)
#
## Train the model using configuration parameters
#model, metrics, feature_importances = train_model(
#    X, y,
#    test_size=training_cfg["test_size"],
#    random_state=training_cfg["random_state"],
#    params=training_cfg.get("params"),
#    num_boost_round=training_cfg["num_boost_round"],
#    early_stopping_rounds=training_cfg["early_stopping_rounds"],
#    seed=training_cfg.get("seed")
#)
#
## Display feature importances
#print("\nFeature Importances:")
#print(feature_importances)
#
## Assuming your trained LightGBM model is stored in the variable `model`
#explainer = shap.TreeExplainer(model)
#shap_values = explainer.shap_values(X)
#
## Plot summary plot
#shap.summary_plot(shap_values, X)
