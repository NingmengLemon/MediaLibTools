import os
import subprocess
import psutil

def linux_escape(text):
    esmap = [
        '$','#',
        '~','.',
        '&','!',
        '^','(',
        ')',' ']
    for es in esmap:
        text = text.replace(es,'\\'+es)
    return text

def check_process():
    for i in psutil.process_iter():
        if i.name() == 'adb.exe':
            return True
    return False

class AdbException(Exception):
    def __init__(self,msg):
        self.msg = msg
    def __str__(self):
        return self.msg

def _popen(cmd):
    p = subprocess.Popen(cmd,shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE)
    stdout,stderr = p.communicate()
    stdout = stdout.decode('utf-8')
    if stderr:
        print(stderr.decode('utf-8'))
    return stdout,stderr

def popen_readline(cmd):
    stdout,stderr = _popen(cmd)
    lines = stdout.split('\r\n')
    for line in lines:
        yield line

def popen_read(cmd):
    stdout,stderr = _popen(cmd)
    return stdout

def check_connect():
    if not check_process():
        rv = os.system('adb devices')
        assert rv==0, 'Abnormal adb return value: %d'%rv
    p = popen_read('adb devices | findstr device')
    ls = p.strip().split('\r\n')
    ls.remove('List of devices attached')
    return [tuple(l.split('\t')) for l in ls]
        
def walk_adb(path):
    root = path
    pipe = popen_readline('adb shell ls -l "%s"'%linux_escape(path))
    head = next(pipe)
    folders = []
    files = []
    if head.startswith('adb.exe:'):
        raise AdbException(head)
    for line in pipe:
        if not line:
            continue
        info = line.split(maxsplit=7)
        #print(info)
        attr, node, user, ugroup, size, mdate, mtime, name = info
        type_ = attr[0]
        if type_ == '-': # 普通文件
            files.append(name)
        elif type_ == 'd': # 目录
            folders.append(name)
    yield (path, folders, files)
    for folder in folders:
        for obj in walk_adb(os.path.join(path,folder).replace('\\','/')):
            yield obj
