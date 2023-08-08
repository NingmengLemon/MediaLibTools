import os
import chardet

path = input('path:')

counter = 0
for root,folders,files in os.walk(path):
    for file in files:
        f = os.path.join(root,file)
        if f.endswith('.lrc'):
            with open(f,'rb') as fp:
                lrc = fp.read()
            try:
                lrc = lrc.decode('utf-8')
            except UnicodeDecodeError:
                continue
            else:
                with open(f,'w+',encoding='MBCS',errors='replace') as fp:
                    fp.write(lrc)
            finally:
                counter += 1
                print('ok.',counter)
print('done.')
os.system('pause')
