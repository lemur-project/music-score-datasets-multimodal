import requests
import os
import json
import tqdm
from utils.my_utils import write_log

ERR_CHANGED_IDS = { # ids that have changed and need to be updated, key is the old id, value is the new id
    "46410016": "464130016",
    "100501322": "990066715",
    "101904": "242327",
    "107896": "107897",
    "200043664": "111673"
}

def parse_data(data, log_file, id):
    """Parse data dynamically by searching for required labels."""
    try:
        summary = data.get("contents", {}).get("summary", [])
        subjects =  data.get("contents", {}).get("subjects", {})
        def find_value_by_label(possible_labels):
            """Search for a label from a list of possible labels and return its associated value."""
            for item in summary:
                if "label" in item and "en" in item["label"]:
                    for label_name in possible_labels:
                        if label_name in item["label"]["en"]:
                            value = item.get("value", {})
                            # if it has languages
                            if "en" in value:
                                value = value.get("en", "Unknown")
                            else:
                                value = value.get("none", "Unknown")
                            return value
            return "Unknown"  # Default if not found

        metadata = {
            "Author": data.get("creator", {}).get("relatedTo", {}).get("label", {}).get("none", ["Unknown"])[0],
            "AuthorID": data.get("creator", {}).get("relatedTo", {}).get("id", "Unknown"),
            "Title": data.get("label", {}).get("en", ["Unknown"])[0],
            "SourceType": find_value_by_label(["Source type"])[0],
            "Year": find_value_by_label(["Dates"])[0].split("-")[0],
            "Key/Mode": find_value_by_label(["Key", "Mode", "Key or mode"])[0],
            "Instruments": find_value_by_label(["Total scoring", "Scoring summary"])[0],
            "RISMID": find_value_by_label(["RISM ID number"])[0],
            "SectionLabel":  subjects.get("sectionLabel", {}).get("en", "Unknown")[0],
            "SectionValues": [item.get("value", "Unknown") for item in subjects.get("items", [])],
        }
        # check if any are unknown
        for key, value in metadata.items():
            if value == "Unknown":
                with open(log_file, "a") as fout:
                    fout.write(f"Missing metadata in {id}: {key}\n")

    except Exception as e:
        with open(log_file, "a") as fout:
            fout.write(f"Error parsing data in {id}: {str(e)[:100]}\n")
        metadata = {"Error": str(e)}

    return metadata


def save_metadata(metadata: dict, output_file: str, log_file: str):
    """Save metadata to a file."""
    # save the metadata to the json file
    try:
        with open(output_file, "w") as fout:
            json.dump(metadata, fout)
    except Exception as e:
        print(f"Error saving metadata to {output_file}: {e}")
        with open(log_file, "a") as fout:
            fout.write(f"Error saving metadata to {output_file}: {str(e)[:100]}\n")
    return output_file
        

def retrieve_metadata(ds_dir: str ="Primus", ids_path: str= "files.lst", log_file: str = "log/retrieve_metadata.log"):
    """Retrieve metadata from a file."""
    if not os.path.exists(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file))

    with open(os.path.join(ds_dir, ids_path), "r") as fin:
        ids = fin.read().splitlines()
            
    # "Accept: application/ld+json" https://rism.online/sources/ID
    for id in tqdm.tqdm(ids, desc="Retrieving metadata"):
        if os.path.exists(os.path.join(ds_dir, id)):
            
            target_file = os.path.join(ds_dir, id, id + ".json")
            # open the target file if it exists
            if os.path.exists(target_file):
                # open the target file
                with open(target_file, "r") as fin:
                    metadata = json.load(fin)
                # if it does not have an error, continue
                if "Error" not in metadata:
                    continue
                
            id = str(int(id.split("-")[0]))
            if id in ERR_CHANGED_IDS:
                id = ERR_CHANGED_IDS[id]
            url = f"https://rism.online/sources/{id}"
            response = requests.get(url, headers={"Accept": "application/ld+json"})
            if response.status_code == 200:
                data = response.json()
                metadata = parse_data(data, log_file, id)
                save_metadata(metadata, target_file, log_file)
            else:
                with open(log_file, "a") as fout:
                    fout.write(f"Resource {id} not found\n")
                metadata = {"Error": "Resource not found"}

                # remove the id from the list if the metadata is not found
                with open(os.path.join(ds_dir, ids_path), "r") as fin:
                    ids = fin.read().splitlines()
                    if id in ids:
                        ids.remove(id)
                with open(os.path.join(ds_dir, ids_path), "w") as fout:
                    fout.write("\n".join(ids))

        else:
            write_log(log_file, f"Directory for ID {id} not found, skipping metadata retrieval.")

    return log_file