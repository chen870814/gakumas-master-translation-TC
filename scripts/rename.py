import os
import re
import glob

filedir = './pretranslate_todo/todo/new/'
pattern = '*.json'

filelist = glob.glob(os.path.join(filedir, pattern))

n=0
for i in filelist:
    oldname = filelist[n]
    newname = re.sub('.json', '_translated.json', filelist[n])
    os.rename(oldname, newname)
    n+=1