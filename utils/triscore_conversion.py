import os
import random
import cv2
import numpy as np
import verovio
from cairosvg import svg2png
import glob
import re
from math import ceil
import os
from utils.abc import mxml2abc
from utils.my_utils import write_log, MXML_FORMATS


def windows_long_path(path):
	if os.name == 'nt':
		if not path.startswith('\\\\?\\'):
			return '\\\\?\\' + os.path.abspath(path)
	return path

def clean_kern_file(kern_file, remove_intruments=False):
	with open(kern_file, 'r') as f:
		kern = f.read()
    
	# Use regex to find and remove lines containing LO:TX:a:t=PT&colon;N (N being a float)
	cleaned_kern = re.sub(r'!LO:TX:a:t=PT&colon;[\d\.]+', '!', kern)
	# Remove lines starting with '!!!'
	cleaned_kern = "\n".join(line for line in cleaned_kern.splitlines() if not line.startswith("!!!"))

	if remove_intruments:
		# remove any line that contain the mark *I (for instrument)
		# split by lines, and then by tabs, and then check if any of the elements in the line starts with *I
		cleaned_kern = "\n".join(
			line for line in cleaned_kern.splitlines() if not any(
				element.startswith('*I') for element in line.split('\t')
			)
		)

	# Write the cleaned kern file
	with open(kern_file, 'w') as f:
		f.write(cleaned_kern)
	return cleaned_kern


def find_image_cut(sample, margin_bot=40, margin_right=40):
	cut_height = None
	cut_width = None

	height, width = sample.shape[:2]

	for y in range(height - 1, -1, -1):
		if [0, 0, 0] in sample[y]:
			cut_height = y + margin_bot
			break

	for x in range(width - 1, -1, -1):
		if [0, 0, 0] in sample[:, x]:
			cut_width = x + margin_right
			break

	return cut_height, cut_width


def rfloat(start, end):
	return round(random.uniform(start, end), 2)


def krn2image(kern_file, img_path, log_file=None):
	kern_file = str(kern_file)
	
	# clean the kern file
	clean_kern_file(kern_file)

	vtk = verovio.toolkit()

	width = 10000
	height = ceil(width * 1.414)
	vtk.setOptions({
		"pageWidth": width,
		"pageHeight": height,
		"scale": 60,
		"footer": 'none',
		'barLineWidth': rfloat(0.3, 0.8),
		'beamMaxSlope': rfloat(10, 20),
		'staffLineWidth': rfloat(0.1, 0.3),
		'spacingStaff': rfloat(4, 12)
	})

	try:
		vtk.loadFile(kern_file)
		svg_content = vtk.renderToSVG()
		svg_content = svg_content.replace("overflow=\"inherit\"", "overflow=\"visible\"")

		png_content = svg2png(bytestring=svg_content, background_color='white', dpi=300)
		png_data = np.frombuffer(png_content, np.uint8)
		png_img = cv2.imdecode(png_data, cv2.IMREAD_UNCHANGED)

		cut_height, cut_width = find_image_cut(png_img)
		if cut_height is not None:
			png_img = png_img[:cut_height, :]
		if cut_width is not None:
			png_img = png_img[:, :cut_width]

		cv2.imwrite(img_path, png_img)
	except Exception as err:
		write_log(log_file, f'{kern_file}: {err}')

	return log_file


def render_kern_files_to_image(ds_dir: str, log_file=None):

	print("Rendering kern files to images in", ds_dir, "please wait...")

	kern_files = glob.glob(os.path.join(ds_dir, '**/*.krn'), recursive=True)
	
	for kern_file_path in kern_files:
		score_dir = os.path.dirname(kern_file_path)
		img_path = os.path.join(score_dir, os.path.basename(kern_file_path).replace('.krn', '.png'))
		print("Rendering", kern_file_path)
		if os.path.exists(img_path):
			continue
		krn2image(
			kern_file_path, 
			img_path, 
			log_file=log_file,
		)

	return log_file

def convert_mxml_files_to_abc(ds_dir, log_file=None):
	
	mxml_paths = glob.glob(f"{os.path.join(ds_dir, '**', '*.musicxml.xml')}", recursive=True)
	print("Converting MXML files to ABC in", ds_dir, "please wait...")

	for mxml_file in mxml_paths: 
		tgt_abc_path = mxml_file.replace(".musicxml.xml", ".abc")
		print("Converting", mxml_file)
		mxml2abc(
			mxml_file=windows_long_path(mxml_file),
			abc_file=windows_long_path(tgt_abc_path),
			log_file=log_file,
		)

