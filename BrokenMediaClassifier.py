import os
import shutil
import subprocess
from PIL import Image,UnidentifiedImageError

workdir = input('Path: ')
broken_dir = input('Broken path: ')
fine_dir = input('Fine path: ')

if not os.path.exists(workdir):
    raise FileNotFoundError()
if not os.path.exists(broken_dir):
    os.makedirs(broken_dir,exist_ok=True)
if not os.path.exists(fine_dir):
    os.makedirs(fine_dir,exist_ok=True)

def subprocessPopen(cmd):
    p = subprocess.Popen(cmd,shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    msg = ''
    for line in p.stdout.readlines():
        msg += line.decode()
    status = p.wait()
    return status

def testImg(file):
    try:
        fp = Image.open(file)
    except:
        return False
    else:
        return True

def testVoA(file):
    return subprocessPopen('ffprobe "{}"'.format(file))==0

fl = os.listdir(workdir)
for file in fl:
    fp = os.path.join(workdir,file)
    endpart = file.split('.')[-1].lower()
    if endpart in ['jpg','png','gif','jpeg','tiff']:
        if testImg(fp):
            shutil.move(fp,fine_dir)
            print('Fine:',file)
        else:
            shutil.move(fp,broken_dir)
            print('Broken:',file)
##    elif endpart in ['mp4','avi','mkv','mov','3gp',
##                     'mp3','ogg','acc','m4a','wav']:
##        if testVoA(fp):
##            shutil.move(fp,fine_dir)
##            print('Fine:',file)
##        else:
##            shutil.move(fp,broken_dir)
##            print('Broken:',file)
