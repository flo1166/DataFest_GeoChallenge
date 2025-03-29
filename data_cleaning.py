import pandas as pd
import numpy as np
import geopandas as gpd

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

    # PLZ zu Stadtbezirk Mapping für München
    muenchen_stadtbezirke = pd.read_csv("Data/Stadtbezirke/muenchen.csv", sep = ';', index_col = 'PLZ')
    muc_bezirk_dict = muenchen_stadtbezirke.to_dict()

    # PLZ-Karte laden und Stadtbezirke zuordnen
    plz_map = pd.read_json("Data/PLZMap/georef-germany-postleitzahl.json")
    plz_map['Stadtbezirk'] = plz_map['plz_code'].apply(lambda x: muc_bezirk_dict['Stadtbezirk'][x] if x in muc_bezirk_dict.keys() else None)

    # Gemeindedaten laden
    df_municipal = pd.read_csv('Data/municipal_main/municipal_main.csv')

    # WICHTIG: Ergebnis des merge zuweisen
    df_municipal = df_municipal.merge(plz_map[['plz_name', 'plz_code', 'Stadtbezirk', 'name']], 
                                    left_on='GEN', right_on='plz_name')

    # ÖPNV-Daten laden und vorbereiten
    geopandas_opnv = gpd.read_file("Data/opnv/opnv_gute_gemeinden_2025.gpkg")
    geopandas_opnv['Gemeinde-schlüssel (AGS)'] = geopandas_opnv['Gemeinde-schlüssel (AGS)'].astype(float)

    # Merge mit ÖPNV-Daten   
    df_municipal = df_municipal.merge(geopandas_opnv[['Gemeinde-schlüssel (AGS)','Name', 'Durch-schnittliche Güte']], 
                                    left_on='AGS', right_on='Gemeinde-schlüssel (AGS)')

    # Überprüfe zuerst die tatsächlichen Spaltennamen
    print(df_municipal.columns)

    # Dann merge mit korrekten Spaltennamen
    # Nutze entweder 'name' oder 'Name' je nachdem was tatsächlich existiert
    return df.merge(df_municipal[['Name', 'Durch-schnittliche Güte', 'GEN']], 
                            left_on='plz', right_on='Name')

def adjust_deflate_columns(df, col_to_deflate, location_cols):
    """
    Adjust the column(s) in `col_to_deflate` by dividing each value by the group's average.
    
    Parameters:
        df (pd.DataFrame): Input DataFrame.
        col_to_deflate (str or list): Column name or list of columns to be adjusted.
        location_cols (list): List of columns defining the grouping.
    
    Returns:
        pd.DataFrame: DataFrame with the adjusted deflation columns.
    """
    group_means = df.groupby(location_cols)[col_to_deflate].transform("mean")
    df[col_to_deflate] = df[col_to_deflate] / group_means
    return df

def transform_date(date_str):
    # Expects date_str of format 'YYYYmM' (e.g. '2007m2')
    try:
        year = int(date_str[:4])
        month = int(date_str.split('m')[1])
        return datetime.date(year, month, 1)
    except (ValueError, IndexError):
        raise ValueError(f"Invalid date format: {date_str}. Expected format 'YYYYmM'.")
    
def display_years(df):
    """
    Returns a new DataFrame with 'adat' and 'edat' columns displayed as 'Year'.

    Parameters:
        df (pandas.DataFrame): DataFrame containing at least columns
                               'adat' and 'edat'.

    Returns:
        pandas.DataFrame: Copy of the input DataFrame with 'adat' and 'edat'
                          replaced by their year value.
    """
    df_copy = df.copy()
    
    def extract_year(date_str):
        try:
            return transform_date(date_str).year
        except Exception:
            return None
    
    df_copy['adat'] = df_copy['adat'].apply(extract_year)
    df_copy['edat'] = df_copy['edat'].apply(extract_year)
    
    return df_copy

