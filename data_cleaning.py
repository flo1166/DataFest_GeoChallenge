import pandas as pd
import numpy as np

# Create a function to merge columns with the same "obid"
def handle_duplicate_ids(df):
    import pandas as pd
    # Step 1: Drop duplicates where all columns except "spell" are a duplicate.
    cols_step1 = [col for col in df.columns if col != "spell"]
    df_step1 = df.drop_duplicates(subset=cols_step1, keep="first")
    
    # Step 2: For rows that are duplicates across all columns
    # except "spell" and "laufzeittage": 
    # average "laufzeittage" and use the first row for the rest.
    cols_group = [col for col in df_step1.columns if col not in ["spell", "laufzeittage"]]
    df_step2 = df_step1.groupby(cols_group, as_index=False).agg({
        "laufzeittage": "mean",
        "spell": "first"
    })
    
    # Step 3: Ensure unique "obid": if the same obid occurs more than once,
    # create a new id by appending a differentiator.
    def make_unique_obids(df):
        new_ids = []
        obid_counts = {}
        for obid in df["obid"]:
            if obid not in obid_counts:
                obid_counts[obid] = 1
                new_ids.append(obid)
            else:
                obid_counts[obid] += 1
                new_ids.append(f"{obid}_{obid_counts[obid]}")
        df["obid"] = new_ids
        return df

    df_final = make_unique_obids(df_step2)
    return df_final

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