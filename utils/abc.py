import os
import subprocess
from unidecode import unidecode


def write_log(log_file, message):
    if log_file is None:
        return
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    with open(log_file, "a", encoding="utf-8") as fout:
        fout.write(message.rstrip() + "\n")


def abc_filter(lines):
    music = ""
    for line in lines:
        if line[:2] in ['A:', 'B:', 'C:', 'D:', 'F:', 'G', 'H:', 'N:', 'O:', 'R:', 'r:', 'S:', 'T:', 'W:', 'w:', 'X:', 'Z:'] \
        or line == '\n' \
        or (line.startswith('%') and not line.startswith('%%score')):
            continue
        else:
            if "%" in line and not line.startswith('%%score'):
                line = "%".join(line.split('%')[:-1])
                music += line[:-1] + '\n'
            else:
                music += line + '\n'
    return music


def mxml2abc(mxml_file, abc_file, xml2abc_script="utils/xml2abc.py", log_file=None):
    """Run the xml->abc converter and return the music string and process object.
    """
    try:
        p = subprocess.Popen(
            [
                "python",
                xml2abc_script,
                "-m",
                "2",
                "-c",
                "6",
                "-x",
                mxml_file,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        output, stderr = p.communicate()
        output = output.replace('\r', '')

        if "fout in:" in output or output.strip() == "":
            write_log(log_file, f"Error processing file {mxml_file}: {output[:200]}")
            return "", p, output + ("\n" + stderr if stderr else "")
        music = unidecode(output).split('\n')
        music = abc_filter(music)

        with open(abc_file, 'w', encoding='utf-8', newline='\n') as f:
            f.write(music)

    except Exception as e:
        write_log(log_file, f"Exception processing file {mxml_file}: {e}")

    return log_file
    
