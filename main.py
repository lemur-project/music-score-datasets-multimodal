from utils import mtd_conversion
from utils import primus_metadata
from utils import primus_conversion, triscore_metadata
from utils import my_utils, triscore_conversion
import fire
import os

def main(ds_name: str, ds_dir: str, log_dir: str = "_conversion_logs"):
    """
    Main function to convert datasets to ABC format. It performs the following steps:
    Args:        
        ds_name (str): Name of the dataset to convert. Must be one of "mtd", "primus", "triscore".
        ds_dir (str): Path to the dataset directory.
        log_dir (str): Name of the subdirectory within the dataset directory where conversion logs will be stored. Default is "_conversion_logs".
    """
    
    if not os.path.exists(ds_dir):
        raise ValueError(f"Dataset directory {ds_dir} does not exist.")
    
    # vague check ds_name matches ds_dir
    if ds_name.lower() not in ds_dir.lower():
        print(f"Warning: dataset name {ds_name} does not seem to match dataset directory {ds_dir}. Please check that the correct dataset name is provided.")
    
    logs_dir = os.path.join(ds_dir, log_dir)
    os.makedirs(logs_dir, exist_ok=True)

    if ds_name == "triscore": 
        
        my_utils.copy_partitions(ds_dir=ds_dir, metadata_folder="./meta/triscore")
        triscore_conversion.render_kern_files_to_image(ds_dir=ds_dir, log_file=os.path.join(logs_dir, "kern2image.log"))
        triscore_conversion.convert_mxml_files_to_abc(ds_dir=ds_dir, log_file=os.path.join(logs_dir, "mxml2abc.log"))
        triscore_metadata.retrieve_metadata(metadata_json_dir= "./meta/triscore/keys", ds_dir=ds_dir, log_file=os.path.join(logs_dir, "muscat_metadata.log"))

    elif ds_name == "mtd":

        my_utils.copy_partitions(ds_dir=ds_dir, metadata_folder="./meta/mtd")
        score_xml_folder =  os.path.join(ds_dir, "data_SCORE_XML")
        score_kern_folder = os.path.join(ds_dir, "data_SCORE_KERN")
        pdf_folder = os.path.join(ds_dir, "data_SCORE_IMG")
        png_folder = os.path.join(ds_dir, "data_SCORE_IMG_PNG")
        mtd_conversion.convert_mxml_files_to_kern(mxml_folder_path=score_xml_folder, kern_folder_path=score_kern_folder, log_file=os.path.join(logs_dir, "mxml2kern.log"))
        mtd_conversion.convert_pdf_files_to_png(pdfs_folder=pdf_folder, png_folder=png_folder, log_file=os.path.join(logs_dir, "pdf2image.log"))

    elif ds_name == "primus":

        my_utils.copy_partitions(ds_dir=ds_dir, metadata_folder="./meta/primus")
        primus_metadata.retrieve_metadata(ds_dir=ds_dir, log_file=os.path.join(logs_dir, "primus_metadata.log"))
        primus_conversion.convert_pae_files_to_kern(ds_dir=ds_dir, log_file=os.path.join(logs_dir, "pae2kern.log"))
        primus_conversion.convert_mei_files_to_abc(ds_dir=ds_dir, log_file=os.path.join(logs_dir, "mei2abc.log"))

if __name__ == "__main__":
    fire.Fire(main)