import pandas as pd
import numpy as np

# Create function for data cleaning
def clean_data(df, columns_for_model):
    # Add spell column to list of columns
    columns_for_model.append(["spell", "obid"])

    # Filter the DataFrame to only include the specified columns
    df = df[columns_for_model]

    # Handle duplicate IDs
    df = handle_duplicate_ids(df)

    # clean the DataFrame
    df = clean_real_estate_df(df)


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


def clean_real_estate_df(df, columns):
    # 1. Define placeholders to treat as missing
    missing_placeholders = [
        "Other missing"
    ]

    # 2. Replace them with np.nan
    df.replace(missing_placeholders, np.nan, inplace=True)

    # 3. Coverting values to relevant datatypes
    df['zimmeranzahl'] = pd.to_numeric(df['zimmeranzahl'], errors='coerce')
    df['obid'] = df['obid'].astype(str)

    filtered_df = df[df['laufzeittage'] <= 365]
    filtered_df = filtered_df.dropna(subset=['energieeffizienzklasse', 'zimmeranzahl'])

    return df

