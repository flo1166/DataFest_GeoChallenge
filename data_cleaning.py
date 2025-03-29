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