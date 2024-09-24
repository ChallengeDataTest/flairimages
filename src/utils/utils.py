# utility functions for fairimages project

import os
import numpy as np
import json
import yaml
import matplotlib.pyplot as plt
from matplotlib.colors import hex2color
from pathlib import Path
from pprint import pprint
import pandas as pd
import skimage.transform as skt
import unittest



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
    class_to_hex = conf['nomenclature']['hex_colors']
    class_to_rgb = np.zeros((len(class_to_hex)+1, 3), dtype=np.uint8)
    for k, v in class_to_hex.items():
        class_to_rgb[k] = (np.array(hex2color(v))*255).astype(np.uint8)
    conf['nomenclature']['class_to_rgb'] = class_to_rgb
    
    # precalculate vegetal classes indicators
    class_to_vegetal = np.zeros(shape=len(class_to_hex)+1, dtype=np.uint8)
    for c in conf['nomenclature']['vegetal_classes']:
        class_to_vegetal[c] = 1
    conf['nomenclature']['class_to_vegetal'] = class_to_vegetal
    
    # precalculate artificiel classes indicators
    class_to_artificial = np.zeros(shape=len(class_to_hex)+1, dtype=np.uint8)
    for c in conf['nomenclature']['artificial_classes']:
        class_to_artificial[c] = 1
    conf['nomenclature']['class_to_artificial'] = class_to_artificial
    
    
    


    if (verbose):
        print(f"Configuration read from {file_path}")
        print(f"file locations are:")
        pprint(conf['paths'])
    return conf
    
    
def get_metadata_to_df(conf:dict) -> pd.DataFrame:
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

def make_samples_df(conf: dict, to_disk:bool=False) -> pd.DataFrame:
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

def make_color_squares(config:dict, output_dir:Path=None, do_plot:bool=True):
    """
    Make a PNG file made of one square per color of the mask convention.
    Name each square with the class color
    """
    
    colors_names = config['nomenclature']['hex_colors']
    class_to_rgb = config['nomenclature']['class_to_rgb']

    labels = config['nomenclature']['classes']['french']
    # for each color in the mask convention
    # make a square of the color
    for k, hex in colors_names.items():
        square = np.zeros((10,10,3), dtype=np.uint8)+class_to_rgb[k]
        # save numpy square as png directly
        
        if output_dir is not None:
            f_out = output_dir/f"sq_{hex[1:]}.png" 
            plt.imsave(f_out, square)
            print(f"Color square {hex} written to {f_out}")
        if do_plot:
            # make the 2x2 cm
            # plot the square
            cm = 1/2.54  # centimeters in inches 
            plt.figure(figsize=(2*cm, 2*cm))
            plt.imshow(square)
            plt.title(f"{k} - {labels[k]}_ {hex}")
            plt.show()
  



    
    

def make_nomenclature_html(config:dict, output_file:Path=None):
    """
    Make an HTML file of the mask convention
    """
    colors = config['nomenclature']['hex_colors']
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


def make_nomenclature_markdown(config:dict, output_file:Path=None):
    """
    Make a markdown file of the mask convention
    """
    hexs = config['nomenclature']['hex_colors']
    labels = config['nomenclature']['classes']['french']   
    artificiel_classes = config['nomenclature']['artificiel']
    vegetal_classes = config['nomenclature']['vegetal']
    out = []
    out.append("| Classe | Label | Color | Artificiel | Végétal |  ")
    out.append("|---|-------|-------|---|---| ")
    for id, label in labels.items():
        hex = hexs[id]
        artificiel = 'A' if id in artificiel_classes else ""
        vegetal = 'V' if id in vegetal_classes else ""
        
        out.append(f"| {id}  | {label} |"+
                   # insert an image from the files prepared by make_color_squares(...)
                   # a notebook is most probably in a level 1 subdirectory of root
                   f"![{hex}](../img/sq_{hex[1:]}.png) |"+
                   f" {artificiel} |"+
                   f" {vegetal} ")
    out = "\n".join(out)
    if output_file is not None:
        # a readme file is most probably the root directory
        saved = out.replace("../img", "./img")
        with open(output_file, 'w') as f:
            f.write(saved)
        print(f"Mask convention written to {output_file}")
    return out




def fast_down_sample(large_images: np.array, by: int, method='max') -> np.array:
    """
    fast downsampling of an array of images by a factor 
    credits to Waylon Flinn
    https://stackoverflow.com/a/56135413/1137334

    convenient for masks (no interpolation)
    """
    # check by is an integer power of 2
    if not int(by) == by and by & (by - 1) != 0:
        raise ValueError("Downsampling factor must be an integer power of 2")

    if len(large_images.shape) != 4:
        raise ValueError("(n_image,W,H,n_channels) shape expected")
    # large image array is shape (1,128, 128, 3)
    # small image array is shape (1,64, 64, 3)
    n, h, w, c = large_images.shape
    if method == 'max':
        small_images = large_images.reshape((n, h//by, by, w//by, by, c)).max(axis=(3, 5))
    elif method == 'corner':
        small_images = large_images[:, ::by, ::by, :]
    elif method == 'mean':
        small_images = large_images.reshape((n, h//by, by, w//by, by, c)).mean(axis=(3, 5))
    elif method == 'nearest':
        # The numpy.reshape function creates a view where possible or a copy otherwise. 
        # see https://numpy.org/doc/stable/user/basics.copies.html
        small_images = skt.resize(large_images.reshape((n*h, w, c)), 
                                  order=0, output_shape=(n*h//by, w//by, c))
        small_images.reshape((n, h//by, w//by, c), inplace=True)
    return small_images
    

def fast_up_sample(small_images: np.array, by: int) -> np.array:
    """
    fast upsampling of an array of images by a factor 
    credits to Waylon Flinn
    https://stackoverflow.com/a/56135413/1137334

    convenient for masks (no interpolation)
    """
    # check by is an integer
    if not int(by) == by and by >= 1:
        raise ValueError("Upsampling factor must be positive integer")

    if len(small_images.shape) != 4:
        raise ValueError("(n_image,W,H,n_channels) shape expected")
    n, h, w, c = small_images.shape
    large_images = np.zeros((n, h*by, w*by, c), dtype=small_images.dtype)
    large_images[:, ::by, ::by, :] = small_images
    return large_images



    

                                    


def class_to_rgb(arr: np.ndarray, config: dict) -> np.ndarray:
    """
    Convert a array indicating class to RGB array
    according to the nomenclature in configuration
    """
    return config['nomenclature']['class_to_rgb'][arr]
    

def class_to_artificial(arr: np.ndarray, conf: dict) -> np.ndarray:
    """
    Convert a array indicating class to an boolean array indicating artificial
    according to the nomenclature in configuration
    """
    return conf['nomenclature']['class_to_artificial'][arr]

def class_to_vegetal(arr: np.ndarray, conf: dict) -> np.ndarray:
    """
    Convert a array indicating class to an boolean array indicating vegetal 
    according to the nomenclature in configuration
    """
    return conf['nomenclature']['class_to_vegetal'][arr]

def vegetal_to_rgb(arr: np.ndarray, conf: dict) -> np.ndarray:
    return np.array(conf['nomenclature']['vegetal_to_rgb'], dtype=np.uint8)[arr]

def artificial_to_rgb(arr: np.ndarray, conf: dict) -> np.ndarray:
    return np.array(conf['nomenclature']['artificial_to_rgb'], dtype=np.uint8)[arr]




