import os
import shutil

WIN_PATH = 1
UNIX_PATH = 2

class TooManyFilesError(Exception):
    def __init__(self, err_msg):
        super().__init__(err_msg)

def create_path(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path
    
def join_paths(*args, sep='/'):
    length = len(args)
    if length == 0:
        return None
    paths = [path.strip() for path in args]
    p = paths[0]
    if length >= 2:        
        for i in range(1, length):
            p2 = paths[i]
            if p2.startswith(sep):
                p2 = paths[i][1:].lstrip()  
            if p.endswith(sep):
                p = p + p2
            else:
                p = p + sep + p2
    return p

def get_os_path(path, os):
    if os == WIN_PATH:
        return path.replace('/','\\')
    else:
        return path.replace('\\','/')

def remove_folder(path):
    if os.path.exists(path) and os.path.isdir(path):
        shutil.rmtree(path)
        
def get_last_pathname(path):
    pos = path.replace('\\', '/').strip().rfind('/')
    if pos >= 0:
        return path[pos+1:]    
    return path

def remove_path_ext(path):
    pos = path.replace('\\', '/').strip().rfind('.')
    if pos >= 0:
        return path[0:pos]    
    return path    

        
if __name__ == "__main__":
    path = 'hello\\there/my.friend'
    print(get_last_pathname(path))
    path = 'hello/world\\this.wonderful'
    print(get_last_pathname(path))
    print(join_paths())
    print(join_paths('/folder/'))
    print(join_paths('/path/', '/ to/', ' this/ ', ' /folder'))
    print(join_paths(' / ', '/', '/ramanujan', '  / ', '/'))
    print(get_os_path('/this\\is/an\\extra/ordinary\\path\\', WIN_PATH))
    print(get_os_path('/this\\is/an\\extra/ordinary\\path\\', UNIX_PATH))
    print(remove_path_ext('this/hello.there'))
    print(remove_path_ext('there/is_will'))