import os
import random
import shutil
import argparse
import json
import logging
from time import *
from pyrebase import pyrebase
from zipfile import ZipFile
from datetime import datetime
from queue import Queue
from queue import Empty
from .RepeatTimer import RepeatTimer as RTimer
from .SimpleFile import *
from .SimpleJson import *

KEEP_ALIVE_TIMEOUT = 5

log = logging.getLogger(__name__)

waiting_queue = Queue()
def stream_listener(message):
    global waiting_queue
    '''
    if message["event"] == 'patch':
        print('event: {}'.format(message["event"])) # put
        print(' path: {}'.format(message["path"])) # /-K7yGTTEp7O549EzTYtI
        print(' data: {}'.format(message["data"])) # {'title': 'Pyrebase', "body": "etc..."}
    '''
    event = message["event"]
    if (event == 'put' or event == 'patch') and message["data"] is not None:
        waiting_queue.put(message)
#        print('>got added: {}<'.format(format(message["data"])))

def open_file(filename):
    try:
        return open(filename)   
    except:
        print(f'Error: The {filename} file is missing.')
    #    log.exception('----------------Log----------------')
        exit(-1)

def start():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("-m", "--main", type=str,
                        help="main Python file to run")
    parser.add_argument("-s", "--server", type=str, nargs='?',
                         default='server_1', help="server name")
    parser.add_argument("-c", "--config", type=str, nargs='?',
                         default='config.json', help="firebase configuration data")
    parser.add_argument("-p", "--profile", type=str, nargs='?',
                         default='profile.json', help="profile data")
    parser.add_argument("-v", "--verbose", action='store_true',
                        help="dump more details")                         
    args = parser.parse_args()

    path_to_upload = os.path.normpath(args.path)
    if not os.path.exists(path_to_upload):
        print(f'Error: the {folder_to_upload} folder does not exist.')
        exit(-1) 

    profile = json.load(open_file(args.profile))
    firebase_config = json.load(open_file(args.config))

    try:
        owner = get_json_value(profile, 'name')
        programme = get_json_value(profile, 'programme')
        for key in ["apiKey", "authDomain", "databaseURL", "storageBucket",
                    "email", "password"]:
            get_json_value(firebase_config, key)
    except JsonFieldError as e:
        print(f'Error: {e.offending_field} field is {e.error_type} in the {profile_filename} file.')
        exit(-1)  

    try:
        firebase = pyrebase.initialize_app(firebase_config)
        auth = firebase.auth()
        user = auth.sign_in_with_email_and_password(get_json_value(firebase_config, "email"),
                                                    get_json_value(firebase_config, "password"))
        db = firebase.database()
        storage = firebase.storage()    
        
    except Exception as e:
        print('An exception has just happened!!!')
    #    print(e)
        log.exception('----------------Log----------------')
        exit(-1)

    if args.verbose:
      print(f'firebase_config = {json.dumps(firebase_config, indent=2)}\n'
            f'profile = {json.dumps(profile, indent=2)}')

    print('Connected to Firebase...')
    my_stream = None
    timer = None
    root = 'auto'
    root = join_paths('auto', args.server)
    path_to_tasks = join_paths(root, 'tasks')
    path_to_tasks_files = join_paths(path_to_tasks, 'files')
    try:        
        fname = get_last_pathname(path_to_upload)
        fname_no_ext = remove_path_ext(fname)
        owner_ = owner.replace(' ', '_')
        date_time = str(strftime('%Y%m%d_%H%M%S'))
        filename = f'{owner_}_{programme}_{date_time}_{fname_no_ext}.zip'
        print(f'Zipping {path_to_upload}...')
        zip_file = fname_no_ext + '.zip'
        target_file = args.main
        if os.path.isdir(path_to_upload):
            if target_file is not None:
                path_to_file = join_paths(path_to_upload, target_file)
                if not os.path.isfile(path_to_file):
                    print(f"Error: '{path_to_file}' file does not exist.")
                    exit(-1)            
            # Zip the folder
            shutil.make_archive(path_to_upload, 'zip', fname)
        else:
            # Zip a single file
            with ZipFile(zip_file,'w') as zip: 
                zip.write(os.path.normpath(path_to_upload), fname)
            target_file = fname    
        print(f'Uploading the zip file to {args.server}...')
        result = storage.child(join_paths(path_to_tasks_files, filename)).put(zip_file, user['idToken'])
    #    print('store file ' + str(result))
        date_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        metadata = {
            'metadata': {
                'file'  : filename,
                'owner' : owner,
                'status': 'new',
                'keepalive': False,
                'timestamp': date_time
            }
        }
        if target_file:
            metadata['metadata']['target'] = target_file
        result = db.child(path_to_tasks).push(metadata, user['idToken'])
        os.remove(zip_file)
        print(f'Done uploading.')
        print('Task ID = {}'.format(result['name']))
        path_to_tasks_id = join_paths(path_to_tasks, result['name'])
        my_stream = db.child(path_to_tasks_id).stream(stream_listener, stream_id="reply")
        
        def timeout():
            db.child(path_to_tasks_id).child('metadata').update({'keepalive':True}, user['idToken'])
        
        timer = RTimer(KEEP_ALIVE_TIMEOUT, timeout)
        counter = 0
        first_time = True
        while True:
            try:
                msg = waiting_queue.get(timeout=10)
                '''
                if first_time:
                    print('Starting...')
                    first_time = False
                    timer.start()
                '''
                data = msg['data']
                if msg['event'] == 'patch':
                    if msg['path'] == '/metadata':
                        if 'status' in data:
                            status = data['status']
                            if status == 'running':
                                timer.start()
                                target = get_dict_value('target', data)
                                if target is None:
                                    target =  target_file
                                print(f"Starting {target}...")                            
                            elif status == 'completed':
                                db.child(join_paths(path_to_tasks_id, '/metadata')).remove(user['idToken'])
                                break                            
                if 'message' in data:
                    print(data['message'], flush=True, end='')
                    db.child(join_paths(path_to_tasks_id, msg['path'])).remove(user['idToken'])
            except Empty:
                counter += 1
                print('waiting for the server to respond ({})'.format(counter))
                db.child(join_paths(path_to_tasks_id, 'metadata')).update({'keepalive':True}, user['idToken'])
            except KeyboardInterrupt:
                status = {'status':'keyboard interrupted'}
                db.child(join_paths(path_to_tasks_id, 'metadata')).update(status, user['idToken'])     
                
    except KeyboardInterrupt:
        print("Keyboard interrupt hit.")
    except Exception as e:
        print(e)
    #    log.exception('----------------Log----------------')
    finally:
        if timer:
            timer.cancel()
        if my_stream is not None:
            try:
                my_stream.close()    
            except:
                pass
