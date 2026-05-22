import os
import shutil

MXML_FORMATS = [".mxml", ".xml", ".musicxml"]

def copy_partitions(ds_dir: str, metadata_folder: str="./meta/primus"):

    # Find folder that starts with "partitions"
    partition_folder_path = None
    if os.path.exists(metadata_folder):
        for folder in os.listdir(metadata_folder):
            if folder.startswith("partitions"):
                partition_folder_path = os.path.join(metadata_folder, folder)
                break
    
    if partition_folder_path is None:
        print(f"No pre-computed partitions found in {metadata_folder}.")
        return
    
    # get just the name of the last folder in the path
    partition_folder = partition_folder_path.split("/")[-1]
    dst = os.path.join(ds_dir, partition_folder)
    
    if os.path.exists(partition_folder_path):
        if os.path.exists(dst):
            print(f"Partition directory {dst} already exists. Skipping copy.")
        else:
            shutil.copytree(partition_folder_path, dst)
            print(f"Copied pre-computed partitions from {partition_folder_path} to {dst}")
    else:
        print(f"No pre-computed partitions found at {partition_folder}.")


    ids_file = os.path.join(metadata_folder, "files.lst")
    if os.path.exists(ids_file):
        shutil.copy(ids_file, os.path.join(ds_dir, "files.lst"))
        print(f"Copied files.lst from {ids_file} to {os.path.join(ds_dir, 'files.lst')}")
    else:
        print(f"No files.lst found in {metadata_folder}.")


def write_log(log_file, message):
	if log_file is None:
		return
	log_dir = os.path.dirname(log_file)
	if log_dir:
		os.makedirs(log_dir, exist_ok=True)
	with open(log_file, 'a', encoding='utf-8') as fout:
		fout.write(message.rstrip() + '\n')


