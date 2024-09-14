# utility functions for fairimages project

import os
import numpy as np
import json
import yaml
from matplotlib.colors import hex2color
from pathlib import Path
from pprint import pprint
import pandas as pd

def read_config(file_path:Path, root_dir:Path, verbose=True) -> dict:
    with file_path.open() as f:
        conf= yaml.safe_load(f)
    # resolve directories
    if root_dir is not None:
        for k, v in conf['paths'].items():
            conf['paths'][k] = root_dir
            for sub in v:
                conf['paths'][k] /= sub
    # precalculate class to RGB mapping
    colors = conf['nomenclature']['colors']
    conf['nomenclature']['class_to_color'] = {k: (np.array(hex2color(v))*255).astype(np.uint8) for k, v in colors.items()}
    
    if (verbose):
        print(f"Configuration read from {file_path}")
        print(f"file locations are:")
        pprint(conf['paths'])
    return conf
    
    
def get_metadata_to_df(conf) -> pd.DataFrame:
    with Path(conf['paths']['metadata']).open('r') as f:
        data = json.load(f)
    
    # Convert JSON data to DataFrame
    df = pd.DataFrame.from_dict(data, orient='index').convert_dtypes()
    df.index.name = 'name'
    return df

    
def read_samples_df(conf: dict) -> pd.DataFrame:
    """
    Read the samples dataframe from disk
    """
    df_file = conf['paths']['files_df']
    df = pd.read_pickle(df_file)
    return df

def make_samples_df(conf: dict, to_disk=False) -> pd.DataFrame:
    """
    Make a sample dataframe of (images, lables) couples 
    """
    dataset_dir = Path(conf['paths']['dataset'])
    
    
    
    df_meta = get_metadata_to_df(conf)
    
    
    # e.g. '.tif'
    ext = conf['image_extension']
    
    df = pd.DataFrame({'name': pd.Series(dtype='str'),
                   'image': pd.Series(dtype='str'),
                   'mask': pd.Series(dtype='str')})
    df.set_index('name', inplace=True)
    
    
    for  file  in dataset_dir.glob("**/*"+ext):
        stem = file.stem
        if '_' not in stem:
            continue
        
        # image files are IMG_XXXX.tif, in various folders
        # mask files are MSK_XXXX.tif
        im_or_mask, num_str = file.stem.split("_")
        name = "IMG_" + num_str 
        if name not in df_meta.index:
            print(f"Image {name} for file {file.stem} not found in metadata")
            continue
        # update the dataframe
        if im_or_mask == "IMG":
            df.at[name, 'image'] = file
        elif im_or_mask == "MSK":
            df.at[name, 'mask'] = file

    # merge df and df1 on the index, by intersection
    # this will drop the rows with missing values
    df = df.merge(df_meta, left_index=True, right_index=True)    
    # make csv file 
    if to_disk:
        csv_file = conf['paths']['files_csv']
        df.to_csv(csv_file)
        print(f"Sample list written to {csv_file}")
        # make pickle file
        df_file = conf['paths']['files_df']
        df.to_pickle(df_file)
        print(f"dataframe written to {df_file}")
        
    return df




def make_nomenclature_html(config, output_file=None):
    """
    Make an HTML file of the mask convention
    """
    colors = config['nomenclature']['colors']
    labels = config['nomenclature']['classes']['french']   
    artificiel_classes = config['nomenclature']['artificiel']
    vegetal_classes = config['nomenclature']['vegetal']
    
    
    out = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
            font-family: Arial, sans-serif;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                table-layout: auto;
            }
            th, td {
                text-align: left;
                border: 1px solid black;
                padding: 8px;
            }
        </style>
    </head>
    <body>"""

    out+="<table><tr><th>Classe</th><th>Label</th><th>Color</th><th>Artificiel</th><th>Végétation</th></tr>"
    out+="\n"

    for id, label in labels.items():
        color = colors[id]
        artificiel = 'X' if id in artificiel_classes else ""
        vegetal = 'X' if id in vegetal_classes else ""
        out+=f"<tr>"
        out+=f"<td>{id}</td><td>{label}</td>"
        out+=f"<td><span style=\"color:{color}; font-size: 20px;\">■</span> {color}</td>"
        out+=f"<td>{artificiel}</td>"
        out+=f"<td>{vegetal}</td>"
        out+="</tr>\n"
    
    out+="</table>\n"
    out+="</body></html>"
    if output_file is not None:
        with open(output_file, 'w') as f:
            f.write(out)
        print(f"Nomenclature table written to {output_file}")
    #
    return out


def make_nomenclature_markdown(config, output_file=None):
    """
    Make a markdown file of the mask convention
    """
    colors = config['nomenclature']['colors']
    labels = config['nomenclature']['classes']['french']   
    artificiel_classes = config['nomenclature']['artificiel']
    vegetal_classes = config['nomenclature']['vegetal']
    out = []
    out.append("| Classe | Label | Color | Artificiel | Végétal |  ")
    out.append("|---|-------|-------|---|---| ")
    for id, label in labels.items():
        color = colors[id]
        artificiel = 'X' if id in artificiel_classes else ""
        vegetal = 'X' if id in vegetal_classes else ""
        out.append(f"| {id}  | {label} |"+
                   f"<span style=\"color:{color}; font-size: 20px;\">■</span> `{color}` |"+
                   f" {artificiel} |"+
                   f" {vegetal} ")
    out = "\n".join(out)
    if output_file is not None:
        with open(output_file, 'w') as f:
            f.write(out)
        print(f"Mask convention written to {output_file}")
    return out




def convert_to_color(arr_2d: np.ndarray, config:dict ) -> np.ndarray:
    arr_3d = np.zeros((arr_2d.shape[0], arr_2d.shape[1], 3), dtype=np.uint8)
    for cls, color in config['nomenclature']['class_to_color'].items():
        arr_3d[arr_2d == cls,:] = color
    return arr_3d


def convert_to_artificiel(arr_2d: np.ndarray, conf: dict ) -> np.ndarray:
    arr_3d = np.zeros((arr_2d.shape[0], arr_2d.shape[1], 3), dtype=np.uint8)
    # termwise sum of booleans
    where = np.sum([arr_2d == c for c in conf['nomenclature']['artificiel']], axis=0)
    where = np.expand_dims(where, axis=-1)
    arr_3d = where* np.array([[[255, 0, 0]]]) + (1-where)* np.array([[[0, 0, 255]]])
    return arr_3d.astype(np.uint8)

def convert_to_vegetal(arr_2d: np.ndarray, conf: dict ) -> np.ndarray:
    where = np.sum([arr_2d == c for c in conf['nomenclature']['vegetal']], axis=0)
    where = np.expand_dims(where, axis=-1)
    arr_3d = where* np.array([[[0, 255, 0]]]) + (1-where)* np.array([[[0, 0, 255]]])
    return arr_3d.astype(np.uint8)
    
    
    
