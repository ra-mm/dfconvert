import json
import os
from .convert import convert_notebook

def convert_dfnotebook(notebook, in_fname, out_fname = None):
    if out_fname == None:
        base_name = os.path.splitext(os.path.basename(in_fname))[0]
        out_fname_file = base_name + '_dfnb' + '.ipynb'
        out_fname = os.path.join(os.path.dirname(in_fname), out_fname_file)
    nb = convert_notebook(notebook)
    with open(out_fname, 'w') as json_file:
        json.dump(nb, json_file)
