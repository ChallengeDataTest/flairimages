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
import skimage.io as skio
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
    meta_df = pd.DataFrame.from_dict(data, orient='index').convert_dtypes()
    meta_df.index.name = 'name'
    # convert the date and time columns to year, month, day, hour, minute
    meta_df['date'] = pd.to_datetime(meta_df['date'])
    meta_df['year'] = meta_df['date'].dt.year
    meta_df['month'] = meta_df['date'].dt.month
    meta_df['day'] = meta_df['date'].dt.day
    meta_df.drop(columns=['date'], inplace=True)
    meta_df['hour'] = meta_df['time'].apply(lambda s:  int(s.split('h')[0]))
    meta_df['minute'] = meta_df['time'].apply(lambda s:  int(s.split('h')[1]))
    meta_df.drop(columns=['time'], inplace=True)
    # convert the camera column to a category
    meta_df['camera'] = meta_df['camera'].astype('category')
    return meta_df

    
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
    #
    for  file  in dataset_dir.glob("**/*"+ext):
        stem = file.stem
        if '_' not in stem:
            continue
        #
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

def make_image_collection(conf: dict,
                           max=None, 
                           verbose=True,
                           downsample=None,
                           down_sample_mask_method='nearest',
                           down_sample_image_method='mean', 
                           sample=True, 
                           to_disk=True)-> np.array:
    file_names = read_samples_df(conf)[['image','mask']]
    file_names.reset_index(drop=True, inplace=True)
    
    if downsample is None:
        downsample = conf['collection_downsample']
    assert(downsample > 0)
    # 
    if max is None:
        max = file_names.shape[0]
    assert(max > 0)
    
    n_to_read = min(max, len(file_names))
    
    if sample:
        file_names = file_names.sample(n_to_read, replace=False)
    else:
        file_names = file_names.head(n_to_read) 
    
    # check the image dimensions are a multiple of downsample
    assert(conf['image_shape'][0]%downsample == 0)
    assert(conf['image_shape'][1]%downsample == 0)
    # put the masks for class, artificial, vegetal in the last 3 channel
    record_shape = (n_to_read,
                    conf['image_shape'][0]//downsample,
                    conf['image_shape'][1]//downsample,
                    conf['image_shape'][2]+3)
    mask_channel = conf['image_shape'][2]
    # make an array of images                
    images = np.zeros(shape=record_shape, dtype=np.uint8)
    if verbose:
        print(f"Reading {n_to_read} images")
        print(f"Images will be downsampled by {downsample}x{downsample}")
        print(f"Collection will be stored in shape {record_shape}")
        print(f"the last 3 channels will be the class, artificial and vegetal masks")
        print(f"expected memory usage: {images.nbytes//1e6:,.0f} megabytes")
        
    
    for i,(image_index,image_file, mask_file) in enumerate(file_names.itertuples(index=True)):
        # check we didn't mess up the index
        image = skio.imread(image_file)
        mask = skio.imread(mask_file)
        # downsample
        # (needs an array of images with channel dimension)
        image = fast_down_sample(np.expand_dims(image, axis=0), by = downsample, method =down_sample_image_method).squeeze(axis=0)
        mask = fast_down_sample(np.expand_dims(mask, axis=(0,-1)), by = downsample, method=down_sample_mask_method).squeeze(axis=(0,-1))
        images[i, :, :, 0:mask_channel] = image
        images[i, :, :, mask_channel] = mask
        # print progress
        if verbose:
            if i % 1000 == 0:
                print(f"Reading image {i} of {n_to_read}")
    
    # calculate the artificial and vegetal masks in one pass

    images[:,:,:,mask_channel+1] = class_to_artificial(arr=images[:,:,:,mask_channel], conf=conf)
    images[:,:,:,mask_channel+2] = class_to_vegetal(arr=images[:,:,:,mask_channel], conf=conf)
    
    
    if to_disk:
        np.save(conf['paths']['image_collection'], images)
        np.save(conf['paths']['image_collection_index'], file_names.index.values)
        if verbose:
            print(f"Image collection written to {conf['paths']['image_collection']}")
            print(f"Image collection indexes written to {conf['paths']['image_collection_index']}")
            
    return images, file_names.index.values

def read_image_collection(conf: dict) -> np.array:
    return np.load(conf['paths']['image_collection']), np.load(conf['paths']['image_collection_index'])

def make_nomenclature_html(conf:dict, output_file:Path=None):
    """
    Make an HTML file of the mask convention
    """
    colors = conf['nomenclature']['hex_colors']
    labels = conf['nomenclature']['classes']['french']   
    artificial_classes = conf['nomenclature']['artificial_classes']
    vegetal_classes = conf['nomenclature']['vegetal_classes']
    
    
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
        artificial = 'X' if id in artificial_classes else ""
        vegetal = 'X' if id in vegetal_classes else ""
        out+="<tr>"
        out+=f"<td>{id}</td><td>{label}</td>"
        out+=f"<td><span style=\"color:{color}; font-size: 20px;\">■</span> {color}</td>"
        out+=f"<td>{artificial}</td>"
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


def make_nomenclature_markdown(conf: dict, output_file: Path = None):
    """
    Make a markdown file of the mask convention
    """
    hexs = conf['nomenclature']['hex_colors']
    labels = conf['nomenclature']['classes']['french']
    artificiel_classes = conf['nomenclature']['artificial_classes']
    vegetal_classes = conf['nomenclature']['vegetal_classes']
    out = []
    out.append("| Classe | Label | Color | Artificiel | Végétal |  ")
    out.append("|---|-------|-------|---|---| ")
    for id, label in labels.items():
        hex = hexs[id]
        artificiel = 'A' if id in artificiel_classes else ""
        vegetal = 'V' if id in vegetal_classes else ""

        out.append(f"| {id}  | {label} |" +
                   # insert an image from the files prepared by make_color_squares(...)
                   # a notebook is most probably in a level 1 subdirectory of root
                   f"![{hex}](../img/sq_{hex[1:]}.png) |" +
                   f" {artificiel} |" +
                   f" {vegetal} ")
    out = "\n".join(out)
    if output_file is not None:
        # a readme file is most probably the root directory
        saved = out.replace("../img", "./img")
        with open(output_file, 'w') as f:
            f.write(saved)
        print(f"Mask convention written to {output_file}")
    return out

def make_nomenclature_image(conf:dict, figsize=None):
    """
    Create an image of the mask convention table and save it as a PNG file.
    """
    hexs = conf['nomenclature']['hex_colors']
    labels = conf['nomenclature']['classes']['french']
    artificial_classes = conf['nomenclature']['artificial_classes']
    class_colors = conf['nomenclature']['class_to_rgb']
    vegetal_classes = conf['nomenclature']['vegetal_classes']
    vegetal_colors = conf['nomenclature']['vegetal_to_rgb']
    artificial_colors = conf['nomenclature']['artificial_to_rgb']

    # Create a table with the class information
    table_text = []
    table_colors = []
    for id, label in labels.items():
        table_text.append([f"{id:02d}: {label}",
                           f"{hexs[id]}",
                           "oui" if id in vegetal_classes else "non" ,
                           "oui" if id in artificial_classes else "non"])
        table_colors.append([[1.0,1.0,1.0],
                             np.array(class_colors[id])/255,
                             np.array( vegetal_colors[id in vegetal_classes])/255,
                             np.array(artificial_colors[id in artificial_classes])/255])
    
    # Create a figure and axis
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis('tight')
    ax.axis('off')

    # Create the table
    table = ax.table(cellText=table_text,
                     cellColours=table_colors,
                     colLabels=["Classe", "Couleur","Vegetal", "Artificiel"],
                     cellLoc='center',
                     loc='center',
                     colWidths=[4,1,1,1])

    # change the color of the black cell of the last class
    table[(len(table_text),1)].set_text_props(color='white')
    # change the alignement of the first column
    for i in range(len(table_text)):
        cell = table[(i+1,0)]
        cell._loc = 'left'
        cell._text.set_horizontalalignment('left')
    # Set the color for the "Color" column
    #for i, row in enumerate(table_data):
    #    color = row[2]
    #    table[(i + 1, 2)].set_facecolor(color)

    # Save the table as a PNG file
    return fig, ax   


def fast_down_sample(large_images: np.array, by: int, method='max') -> np.array:
    """
    fast downsampling of an array of images by a factor 
    credits to Waylon Flinn
    https://stackoverflow.com/a/56135413/1137334

    convenient for masks (no interpolation)
    """
    # check by is a positive  integer 
    if int(by) != by  or by < 1:
        raise ValueError("Downsampling factor must be an integer power of 2")

    if len(large_images.shape) != 4:
        raise ValueError("(n_image,W,H,n_channels) shape expected")
    # large image array is shape (1,128, 128, 3)
    # small image array is shape (1,64, 64, 3)
    n, h, w, c = large_images.shape
    
    if  h%by != 0 or w%by != 0:
        raise ValueError("Image dimensions must be a multiple of the downsampling factor")

    if method == 'max':
        small_images = large_images.reshape((n, h//by, by, w//by, by, c)).max(axis=(2, 4))
    elif method == 'corner':
        small_images = large_images[:, ::by, ::by, :]
    elif method == 'mean':
        # warning:  .mean(axis=(2, 4), dtype=large_images.dtype) fails the tests. 
        # Why ?
        # using instead: .mean(axis=(2, 4)).astype(large_images.dtype)
        small_images = large_images.reshape((n, h//by, by, w//by, by, c)).mean(axis=(2, 4)).astype(large_images.dtype)
    elif method == 'nearest':
        # The numpy.reshape function creates a view where possible or a copy otherwise. 
        # see https://numpy.org/doc/stable/user/basics.copies.html
        small_images = skt.resize(large_images.reshape((n*h, w, c)), 
                                  order=0,
                                  output_shape=(n*h//by, w//by, c))
        small_images=small_images.reshape((n, h//by, w//by, c))
    else:
        raise ValueError("method must be 'max', 'corner', 'mean' or 'nearest'")
    return small_images
    

def fast_up_sample(small_images: np.array, by: int) -> np.array:
    """
    fast upsampling of an array of images by a factor 
    credits to Waylon Flinn
    https://stackoverflow.com/a/56135413/1137334

    convenient for masks (no interpolation)
    """
    # check by is an integer
    if  int(by) != by or by < 1:
        raise ValueError("Upsampling factor must be positive integer")

    if len(small_images.shape) != 4:
        raise ValueError("(n_image,W,H,n_channels) shape expected")
    # n, h, w, c = small_images.shape
    # large_images = np.zeros((n, h, by, w, by, c), dtype=small_images.dtype)
    # large_images[:, ::by, ::by, :] = small_images
    return np.repeat(np.repeat(small_images, by, axis=1), by, axis=2)



    

                                    


def class_to_rgb(arr: np.ndarray, conf: dict) -> np.ndarray:
    """
    Convert a array indicating class to RGB array
    according to the nomenclature in configuration
    """
    return conf['nomenclature']['class_to_rgb'][arr]
    

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

def vegetal_to_rgb(arr: np.ndarray, conf: dict, alpha=None) -> np.ndarray:
    res = np.array(conf['nomenclature']['vegetal_to_rgb'], dtype=np.uint8)[arr]
    if alpha is not None:
        res = np.concatenate([res, int(alpha*255)*arr[:,:,np.newaxis]], axis=-1)
    return res

def artificial_to_rgb(arr: np.ndarray, conf: dict, alpha=None) -> np.ndarray:
    res = np.array(conf['nomenclature']['artificial_to_rgb'], dtype=np.uint8)[arr]
    if alpha is not None:
        res = np.concatenate([res, int(alpha*255)*arr[:,:,np.newaxis]], axis=-1)
    return res




