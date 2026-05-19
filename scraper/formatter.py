import json

BC_JSON_OUTPUT_FILE = "bandcamp_results.json"
ALBUM_INFO_TMP = "tmp/album_info.json"

def read_bc_output_file():
  with open(BC_JSON_OUTPUT_FILE, "r") as f:
    data = json.load(f)
  return data

def read_tmp_album_info():
  with open(ALBUM_INFO_TMP, "r") as f:
    data = json.load(f)
  return data