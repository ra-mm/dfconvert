import json
import redbaron
import sys
import re
import os, binascii

#filename = str(sys.argv[1])
fullpath = os.getcwd()
with open(filename) as json_data:
    d = json.load(json_data)

for cell in d['cells']:
    if(cell['cell_type'] != "code"):
        continue
    nlist = ""
    mlist = []
    exec_count = int(binascii.b2a_hex(os.urandom(6)),16)
    for line in cell['source']:
        if(line[0] == '%'):
            mlist.append(line+'\n')
            continue
        elif(re.search('###Out_[0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f]###',line) != None):
            exec_count = int(re.search('(?<=###Out_)[0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f](?<!###)',line).group(0),16)
            continue
        nlist =  nlist + line.rstrip() + '\n'
    nlist = redbaron.RedBaron(nlist)
    for node in nlist.find_all("name",value=lambda value: re.search('(?<=Out_)'+hex(exec_count)[2:],value)):
        try:
            val = nlist.index(node.parent)
        except ValueError:
            pass
        del nlist[val]
    for node in nlist.find_all("name",value=lambda value: re.search('(?<=Out_)[0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f]',value)):
        node.value = "Out['"+str(node.value)[len("Out_"):]+"']"
    cell['execution_count'] = exec_count
    if(len(cell['outputs']) > 0):
        cell['outputs'][0]['execution_count'] = exec_count
    for x in range(len(nlist)):
        mlist.append((nlist[x].dumps()) + '\n')
    cell['source'] = mlist


if(re.search('_ipy',filename) != None):
    ipy = str.index(filename,'_ipy')
    filename = filename[:ipy] + filename[ipy+len('_ipy'):]
filename = fullpath + '\' + filename[:-6] + "_dfpy" + filename[-6:]
with open(filename, 'w') as outfile:
    json.dump(d,outfile,indent=4)
