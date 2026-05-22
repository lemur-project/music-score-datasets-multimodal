
import os
import subprocess
import os
import glob
import pymupdf
from utils.abc import mxml2abc
from utils.my_utils import write_log, MXML_FORMATS

possible_errors_Musicxml_to_Kern = ["Error:", "Error: layer index is -2", "Error: Inconsistent rhythm analysis", 
                       "FORWARD WITH A SMALL VALUE", " fields,    but found ", 
                       "Error: part-list count does not match part count 1 compared to 2",
                       "Error: cannot find partlist", "ERROR: Negative duration",
                       "terminate called after throwing an instance of 'std::out_of_range'",
                       "Unknown part grouping symbol:"]
 
warnings = ["warning: Encountered unprocessed marker", "Warning, replacing existing token:",
            "warning: Cannot have a slur inside another slur",
            "warning", "Warning", ".abc written with"]

MUSICXML2HUM = "/humlib/bin/musicxml2hum"

def add_error(error, dict_errors, file):
    if error not in dict_errors:
        dict_errors[error] = [] 
    dict_errors[error].append(file)

    return dict_errors


def classify_error(error, dict_errors, file, possible_errors):
    bool_error, only_warning = False, False

    try:
        int(error)
        dict_errors = add_error(str(error), dict_errors, file)
        bool_error = True
    except ValueError:
        for error_type in possible_errors:
            if error_type in error:
                dict_errors = add_error(error_type, dict_errors, file)
                bool_error = True
        for warning in warnings:
            if warning in error:
                dict_errors = add_error(warning, dict_errors, file)
                only_warning = True

    if not only_warning and not bool_error:
        dict_errors = add_error("Error code but no error", dict_errors, file)

    return dict_errors, only_warning and not bool_error


def musicxml2kern(mxml_file, tgt_kern_path, log_file=None):
    errors = {}
    
    try:
        result = subprocess.run([MUSICXML2HUM, mxml_file], check=True, text=True, capture_output=True)
        if result.stderr != '':
            print("Error in file:", mxml_file)
            errors, onlyWarnings = classify_error(result.stderr, errors, mxml_file, possible_errors_Musicxml_to_Kern)
            write_log(log_file, f"{mxml_file}: {result.stderr.strip()}")
    except subprocess.CalledProcessError as e:
        err = e.stderr if e.stderr != '' else e.returncode
        errors, onlyWarnings = classify_error(err, errors, mxml_file, possible_errors_Musicxml_to_Kern)
        print("Error in file:", mxml_file)
        write_log(log_file, f"{mxml_file}: {err}")
    except Exception as e:
        write_log(log_file, f"{mxml_file}: {e}")
        

    # Create subdirectories in case not exist
    subdirectories = "/".join(tgt_kern_path.split("/")[:-1]) + "/"
    os.makedirs(os.path.dirname(subdirectories), exist_ok=True)
    
    os.system(MUSICXML2HUM + " '" + mxml_file + "' > '" + tgt_kern_path + "'")

    return tgt_kern_path, errors

def pdf2image(pdf_path, img_path, log_file=None):
    errors = {}
    
    try:
        pages = pymupdf.open(pdf_path)
        if len(pages) == 1:
            page = pages[0]
        else:
            raise ValueError(f"Multiple {len(pages)} pages found in PDF {pdf_path}, expected single-page PDFs.")
        # Save the image
        pix = page.get_pixmap(dpi=200)
        pix.save(img_path)
    
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        write_log(log_file, f"{pdf_path}: {e}")
        return img_path, f"ERR: {str(e)}"
    
    return img_path, errors


#  MTD IS STRUCTURED IN FOLDERS PER FORMAT AND MODALITY, SO CONVERT FOLLOWING THAT STRUCTURE

def convert_pdf_files_to_png(pdfs_folder: str, png_folder: str, log_file=None):
    # Get all the .pdf files in the dataset
    pdf_paths = glob.glob(os.path.join(pdfs_folder, '**/*.pdf'), recursive=True)

    os.makedirs(png_folder, exist_ok=True)

    print("Converting PDF files to images in", pdfs_folder, "please wait...")

    for pdf_file_path in pdf_paths:
        target_path = pdf_file_path.replace(pdfs_folder, png_folder)
        target_path = target_path.replace(".pdf", ".png")
        result_path, errors = pdf2image(pdf_file_path, target_path, log_file=log_file)
        
    return result_path, errors

def convert_mxml_files_to_kern(mxml_folder_path, kern_folder_path, log_file=None):
    
    print("Converting MXML files to Kern in", mxml_folder_path, "please wait...")

    mxml_formats = MXML_FORMATS
    mxml_paths = []
    for format in mxml_formats:
        mxml_paths.extend(glob.glob(f"{os.path.join(mxml_folder_path, '**', '*' + format)}", recursive=True))
        
    for mxml_file in mxml_paths: 
        # replace folder and formats in target path
        tgt_kern_path = mxml_file.replace(mxml_folder_path, kern_folder_path)
        for format in mxml_formats:
            if format in tgt_kern_path:
                tgt_kern_path = tgt_kern_path.replace(format, ".krn")
                break
        print("Converting", mxml_file)
        musicxml2kern(mxml_file, tgt_kern_path, log_file=log_file)

def convert_mxml_files_to_abc(mxml_folder_path, abc_folder_path, log_file=None):
    mxml_formats = MXML_FORMATS
    mxml_paths = []
    for format in mxml_formats:
        mxml_paths.extend(glob.glob(f"{os.path.join(mxml_folder_path, '**', '*' + format)}", recursive=True))
    
    print("Converting MXML files to ABC in", mxml_folder_path, "please wait...")

    for mxml_file in mxml_paths: 
        print("Converting", mxml_file)

        # replace folder and formats in target path
        tgt_abc_path = mxml_file.replace(mxml_folder_path, abc_folder_path)
        for format in mxml_formats:
            if format in tgt_abc_path:
                tgt_abc_path = tgt_abc_path.replace(format, ".abc")
                break
        music, proc, stderr = mxml2abc(mxml_file, log_file=log_file)
        if music:
            os.makedirs(os.path.dirname(tgt_abc_path), exist_ok=True)
            with open(tgt_abc_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(music)
        else:
            write_log(log_file, f"No ABC output for {mxml_file}; stderr: {stderr}")


