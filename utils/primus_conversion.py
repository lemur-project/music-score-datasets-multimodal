import os, subprocess
from utils.abc import mxml2abc
from utils.my_utils import write_log

PAE2KERN = "/humextra/bin/pae2kern"

def format_pae_file(rism_id, pae_file):
    # retrieve the raw data from the pae file
    with open(pae_file, "r") as f:
        pae_data = f.read()
    
    def parse_clef(pae_data):
        return pae_data.split("@")[0].split("%")[-1]
    
    def parse_key_sig(pae_data):
        return pae_data.split("$")[-1].split("ü")[0]

    def parse_time_signature(pae_data):
        return pae_data.split("@")[-1].split("$")[0]
    
    def parse_data(pae_data):
        return "'" + pae_data.split()[-1] + "'"
    
    clef = parse_clef(pae_data)
    key_sig = parse_key_sig(pae_data)
    time_sig = parse_time_signature(pae_data)
    pae_data = parse_data(pae_data)
    pae_data = f"""@start: {rism_id}\n@clef: {clef}\n@keysig: {key_sig}\n@timesig: {time_sig}\n@alttimesig:\n@data: {pae_data}\n@end: {rism_id}\n"""
    return pae_data
    

def rismpae2kern(primus_sample_folder, target_file_path, log_file=None):
    errors = {}
    
    try:
        pae_file = primus_sample_folder + "/" + "regular_pae.pae"
        pae_data = format_pae_file(primus_sample_folder.split("/")[-1], pae_file)

        # create a new pae file with the corresponding filename
        new_pae_file = target_file_path.replace(".krn", ".pae")
        with open(new_pae_file, "w") as f:
            f.write(pae_data)
        command = f'{PAE2KERN} -d "{os.path.dirname(target_file_path)}/" "{new_pae_file}"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.stderr != "":
            write_log(log_file, f"{pae_file}: {result.stderr.strip()}")
    except Exception as e:
        write_log(log_file, f"{pae_file}: {e}")

    return target_file_path, errors


def mei2mxml(mei_path, xml_path, log_file=None):
    try:
        p = subprocess.Popen(
            'python -m converter21 -f mei -t musicxml -c "' + mei_path + '" "' + xml_path + '"',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        )
        result = p.communicate()
        if result[0] != b'':
            write_log(log_file, f"Failed converting MEI {mei_path} -> XML {xml_path}: {result[0].decode('utf-8').strip()}")
        return result
    except Exception as e:
        write_log(log_file, f"Failed converting MEI {mei_path} -> XML {xml_path}: {e}")
        return None


def convert_pae_files_to_kern(ds_dir, log_file=None):
    
    print("Converting PriMus paes to kern in", ds_dir, "please wait...")
    for dirpath, dirnames, filenames in os.walk(ds_dir):
        for dirname in dirnames:
            subdir_path = os.path.join(dirpath, dirname)
            target_path = subdir_path + "/" + dirname + ".krn"
            if os.path.exists(target_path): 
                continue    
            
            # there should be a single pae file in the subdir, if not, skip (folder contains non-score data)
            files = os.listdir(subdir_path)
            pae_files = [f for f in files if f.endswith(".pae")]
            if len(pae_files) == 0:
                continue
            elif len(pae_files) > 1:
                write_log(log_file, f"Multiple PAE files found in {subdir_path}, expected one PAE file per score. Skipping this folder.")
                continue
            else:
                rismpae2kern(subdir_path, target_path, log_file=log_file)

    return log_file


def convert_mei_files_to_abc(ds_dir, log_file=None):
    
    print("Converting PriMus MEI files to ABC in", ds_dir, "please wait...")

    for dirpath, dirnames, filenames in os.walk(ds_dir):
        for dirname in dirnames:
            subdir_path = os.path.join(dirpath, dirname)
            
            # find all mei files (should be one)
            files = os.listdir(subdir_path)
            mei_files = [f for f in files if f.endswith(".mei")]
            if len(mei_files) == 0:
                continue
            elif len(mei_files) > 1:
                write_log(log_file, f"Multiple MEI files found in {subdir_path}, expected one MEI file per score. Skipping this folder.")
                continue
            mei_file = os.path.join(subdir_path, mei_files[0])
            xml_file = mei_file.replace(".mei", ".xml")
            abc_file = mei_file.replace(".mei", ".abc")
            mei2mxml(mei_file, xml_file, log_file=log_file)
            mxml2abc(xml_file, abc_file, log_file=log_file)

    return log_file
      


