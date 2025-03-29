import pandas as pd
import numpy as np

# Create function for data cleaning
def clean_data(df, columns_for_model):
    # Add spell column to list of columns
    columns_for_model.append("spell")
    columns_for_model.append("obid")

    # Filter the DataFrame to only include the specified columns
    df = df[columns_for_model]

    # Handle duplicate IDs
    df = handle_duplicate_ids(df)

    # clean the DataFrame
    df = clean_real_estate_df(df)

    return df


# Create a function to merge columns with the same "obid"
def handle_duplicate_ids(df):
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


def clean_real_estate_df(df):
    # 1. Define placeholders to treat as missing
    missing_placeholders = [
        "Other missing"
    ]

    # 2. Replace them with np.nan
    df.replace(missing_placeholders, np.nan, inplace=True)

    # 3. Coverting values to relevant datatypes
    df['zimmeranzahl'] = pd.to_numeric(df['zimmeranzahl'], errors='coerce')

    filtered_df = df[df['laufzeittage'] <= 365]

    # Drop "spell" and "obid" columns
    df = filtered_df.drop(columns=['spell', 'obid'], errors='ignore')

    # Drop rows with missing values
    df  = df.dropna()

    return df

def map_municipality_df(df):
    '''
    This function loads the municipal data, loads the plz and adds it to the df.
    '''
    muenchen_stadtbezirke = pd.read_csv("Data/Stadtbezirke/muenchen.csv", sep = ';', index_col = 'PLZ')
    muc_bezirk_dict = muenchen_stadtbezirke.to_dict()

    df_municipal = pd.read_csv('Data/municipal_main/municipal_main.csv')
    plz_map = pd.read_json("Data/PLZMap/georef-germany-postleitzahl.json")
    plz_map['Stadtbezirk'] = plz_map['plz_code'].apply(lambda x: muc_bezirk_dict['Stadtbezirk'][x] if x in muc_bezirk_dict.keys() else None)
    df_municipal.merge(plz_map[['plz_name', 'plz_code', 'Stadtbezirk']], left_on = 'GEN', right_on = 'plz_name')
    return df.merge(df_municipal, left_on = 'plz', right_on = 'plz_name')
