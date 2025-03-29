
import pandas as pd
import numpy as np


def load_and_clean_csv(filepath):
    df = pd.read_csv(filepath)
    cleaned_df = clean_real_estate_df(df)
    return cleaned_df


df = pd.read_csv("/Users/fannibuki/Documents/Datafest/HiDrive/panel 2/CampusFile_WM_cities.csv")
columns_for_model = [
    'obid', 'spell', 'laufzeittage', 'mietekalt', 'rent_sqm',
    'zimmeranzahl', 'wohnflaeche', 'objektzustand',
    'energieausweistyp', 'energieeffizienzklasse',
    'heizungsart', 'gid2019', 'kid2019'
]

# Filter the original DataFrame
df = df[columns_for_model]
df.head()
df.dtypes

# 1. Define placeholders to treat as missing
missing_placeholders = [
    "Other missing"
]

# 2. Replace them with np.nan
df.replace(missing_placeholders, np.nan, inplace=True)

df['column_name'].unique()

# 3. Convert columns to numeric where possible
for col in df.columns:
    if col != "plz" and df[col].dtype == "object":
        try:
            df[col] = pd.to_numeric(df[col])
        except:
            pass  # leave non-numeric text columns unchanged

df.describe()




def clean_real_estate_df(df):


    return df