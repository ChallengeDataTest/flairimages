# utility functions for fairimages project

import os
import json
import zipfile
import requests
import shutil

DATA_URLS = {
    "toy_dataset": "https://storage.gra.cloud.ovh.net/v1/AUTH_366279ce616242ebb14161b7991a8461/defi-ia/flair_data_1/flair_1_toy_dataset.zip",
    "aerial_train": "https://storage.gra.cloud.ovh.net/v1/AUTH_366279ce616242ebb14161b7991a8461/defi-ia/flair_data_1/flair_aerial_train.zip",
    "aerial_test": "https://storage.gra.cloud.ovh.net/v1/AUTH_366279ce616242ebb14161b7991a8461/defi-ia/flair_data_1/flair_1_aerial_test.zip",
    "labels_train": "https://storage.gra.cloud.ovh.net/v1/AUTH_366279ce616242ebb14161b7991a8461/defi-ia/flair_data_1/flair_labels_train.zip",
    "labels_test": "https://storage.gra.cloud.ovh.net/v1/AUTH_366279ce616242ebb14161b7991a8461/defi-ia/flair_data_1/flair_labels_test.zip",
    "aerial_shapes":"https://storage.gra.cloud.ovh.net/v1/AUTH_366279ce616242ebb14161b7991a8461/defi-ia/flair_data_1/flair-1_metadata_aerial.zip",
    "aerial_metadata":"https://storage.gra.cloud.ovh.net/v1/AUTH_366279ce616242ebb14161b7991a8461/defi-ia/flair_data_1/flair_1_toy_dataset.zip"
}

def get_image_paths(image_dir):
    """
    Get all image paths in a directory
    """
    image_paths = []
    for root, dirs, files in os.walk(image_dir):
        for file in files:
            if file.endswith('.jpg') or file.endswith('.png'):
                image_paths.append(os.path.join(root, file))
    return image_paths





def download_data(data_dir, type='toy', re_download=False, no_write=True):
    """
    Download data
    """
    if type not in ["toy", "test", "train", "meta"]:
        raise ValueError("type must be one of 'toy', 'test', 'train', 'meta'")  
    if type != "toy":
        raise NotImplementedError("Only toy data download is available at the moment")
    
    if not os.path.exists(data_dir):
        raise ValueError(f"Directory {data_dir} does not exist")
        
    if type == "toy":
        url = DATA_URLS['toy_dataset']
        toy_dataset_zip_filename = url.split("/")[-1]
        toy_dataset_dir_name = toy_dataset_zip_filename.split(".")[-2]
        toy_dataset_dir = os.path.join(data_dir, toy_dataset_dir_name)
        toy_dataset_zip_path = os.path.join(data_dir, toy_dataset_zip_filename)

        if not no_write:
            do_download = True
            if os.path.exists(toy_dataset_zip_path):
                if re_download:
                    os.remove(toy_dataset_zip_path)
                    print(f"Existing {toy_dataset_zip_path} removed")
                    do_download = True
                else:
                    print(f"{toy_dataset_zip_path} already exists. Set re_download=True to download again")
                    do_download = False
            
            if do_download:
                print(f"downloading {toy_dataset_zip_path}")
                response = requests.get(url)
                with open(toy_dataset_zip_path, 'wb') as f:
                    f.write(response.content)
                print("Zip file downloaded successfully: {toy_dataset_zip_path}")

            # unzip the file
            
            # check if the directory already exists
            if os.path.exists(toy_dataset_dir):
                # remove the existing directory
                shutil.rmtree(toy_dataset_dir)
                print(f"Existing {toy_dataset_dir} removed")
            with zipfile.ZipFile(toy_dataset_zip_path, 'r') as zip_ref:
                zip_ref.extractall(path=toy_dataset_dir)
            print(f"Zip file extracted successfully into {toy_dataset_dir}")
        
    return toy_dataset_dir
    

def make_sample_table(dataset_dir, sample_list_file=None, no_write=True):
    """
    Make a sample table of (images, lables) couples 
    """
    # 
    # make a flat list of all files in the dataset directory
    if sample_list_file is None:
        sample_list_file = os.path.join(dataset_dir, "sample_list.csv") 

    if not no_write:    
        all_images = {}
        all_masks = {}
        for root, dirs, files in os.walk(dataset_dir):
            for file in files:
                # for instance IMG_061946.tif
                # the key is 061946         
                im_or_mask, key = file.split(".")[-2].split("_")
                if im_or_mask == "IMG":
                    all_images[key] = os.path.join(root, file)
                elif im_or_mask == "MSK":
                    all_masks[key] = os.path.join(root, file)
        #    
        # make csv file of (key, im, msk triplets), sorted by key
        with open(sample_list_file, 'w') as f:
            f.write("KEY, IMG, MSK\n")
            for key in sorted(list(all_images.keys())):
                # this is to prevent csv reading to interpret the key as a number
                # with the risk of losing leading zeros and creating collisions
                txt_key = 'I'+key
                f.write(f"{txt_key},{all_images[key]},{all_masks[key]}\n")
        print(f"Sample list written to {sample_list_file}")

    return sample_list_file

    
    
