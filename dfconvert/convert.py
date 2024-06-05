import asttokens
from . import make_ipy
from .topological import topological
from IPython.core.inputtransformer2 import TransformerManager
from .display_cell import display_variable_cell 

def convert_notebook(notebook):
    code_cells_ref = dict()
    non_code_cells_ref = dict()
    uuids_downlinks = dict()
    uuids_output_tags = dict()
    non_code_cells_block = dict()
    non_code_cells_seq = dict()
    transformer_manager = TransformerManager()
    valid_output_tags = dict()
    latest_non_code_cell = None
    for cell in notebook['cells']:
        output_tags = list()
        id = cell['id'].split('-')[0]
        if cell['cell_type'] != "code":
            non_code_cells_seq[id] = []
            if latest_non_code_cell is not None and len(non_code_cells_block[latest_non_code_cell]) == 0:
                del non_code_cells_block[latest_non_code_cell]
                non_code_cells_seq[id] += non_code_cells_seq[latest_non_code_cell] + [non_code_cells_ref[latest_non_code_cell]]
                del non_code_cells_seq[latest_non_code_cell]

            latest_non_code_cell = id
            non_code_cells_ref[id] = cell
            non_code_cells_block[id] = set()

        else:
            if latest_non_code_cell is not None and len(cell['source']) > 0:
                non_code_cells_block[latest_non_code_cell].add(id)
            valid_output_tags[id] = []
            for output in cell['outputs']:
                if output.get('metadata') and output['metadata'].get('output_tag'):
                    output_tags.append(output['metadata']['output_tag'])
                    output['execution_count'] = None
                    valid_output_tags[id].append(output['metadata']['output_tag'])
                elif output.get('data') and output['data'].get('text/plain'):
                    output['execution_count'] = None

            if len(cell['outputs']) > 0:
                cell['outputs'][0]['execution_count'] = None
            cell['execution_count'] = None
            uuids_output_tags[id] = output_tags
            code_cells_ref[id] = cell
    
    for uuid, cell in code_cells_ref.items():
        make_ipy.ref_uuids = set()
        code= transformer_manager.transform_cell(cell['source'])
        code = make_ipy.convert_dollar(code, make_ipy.identifier_replacer, {})
        code = make_ipy.convert_identifier(code, make_ipy.dollar_replacer)
        code = make_ipy.convert_output_tags(code, uuids_output_tags[uuid], uuid, code_cells_ref.keys())

        cast = asttokens.ASTTokens(code, parse=True)
        code = make_ipy.transform_out_refs(code, cast)
        
        cast = asttokens.ASTTokens(code, parse=True)
        code = make_ipy.transform_last_node(code, cast, uuid)

        #Create list of all out_tags
        valid_tags = []
        if ('outputs' in cell):
            for output in cell['outputs']:
                if ('metadata' in output and 'output_tag' in output['metadata']):
                    valid_tags.append(output['metadata']['output_tag'])

        cast = asttokens.ASTTokens(code, parse=True)
        code, out_targets = make_ipy.out_assign(code, cast, uuid, valid_tags)
        
        code_cells_ref[uuid]['source'] = code.strip()
        
        #add print statement end of each code
        if uuids_output_tags.get(uuid):
            exported_variables = '{ '
            for value in uuids_output_tags[uuid]:
                if len(value) >= 8 and (value[:8] in code_cells_ref.keys() or uuid == value[:8]):
                    continue
                exported_variables += f'"{value}_{uuid}": {value}_{uuid},'
            exported_variables += '}'
            
            if len(exported_variables) > 3:
                code += '\ndisplay_variables(' + exported_variables + ')'
            else:
                if ('Out_'+uuid) in code:
                    exported_variables = f'"Out_{uuid}": Out_{uuid},'
                    code += '\ndisplay_variables( { ' + exported_variables + ' })'
        else:
                if ('Out_'+uuid) in code:
                    exported_variables = f'"Out_{uuid}": Out_{uuid},'
                    code += '\ndisplay_variables({ ' + exported_variables + ' })'

        code_cells_ref[uuid]['source'] = code

        uuids_downlinks[uuid] = [id for id in make_ipy.ref_uuids]
    
    sorted_order = list(topological(uuids_downlinks))
    ordered_cells = list()

    for cell_id in sorted_order[::-1]:
        for id, code_ids in non_code_cells_block.items():
            if cell_id in code_ids:
                if non_code_cells_seq.get(id):
                    ordered_cells += non_code_cells_seq[id]
                ordered_cells.append(non_code_cells_ref[id])
                del non_code_cells_block[id]
                break
        ordered_cells.append(code_cells_ref[cell_id])

    for cell_id in non_code_cells_block.keys():
        ordered_cells.append(non_code_cells_ref[cell_id])

    notebook['cells'] = display_variable_cell + ordered_cells

    if notebook.get('metadata') and notebook['metadata'].get('kernelspec'):
        if notebook["metadata"]["kernelspec"].get('display_name'):
            notebook["metadata"]["kernelspec"]["display_name"] = "Python 3"
        if notebook["metadata"]["kernelspec"].get('name'):
            notebook["metadata"]["kernelspec"]["name"] = "python3"


    return notebook
