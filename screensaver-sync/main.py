import requests
import os
import hashlib

base_url = 'https://cdn.jsdelivr.net/gh/mzlogin/kindle-paperwhite-screensavers@built/'
screensaver_path = '/mnt/us/linkss/screensavers/'
log_row_begin = 10
log_row_end = 30
log_row = 10

def show_msg(text):
    global log_row
    print(text)
    log_row += 1
    if log_row > log_row_end:
        log_row = log_row_begin
    os.system('eips 10 %d "%s"' % (log_row, text))

def get_file_md5(file_path):
    with open(file_path, 'rb') as f:
        md5obj = hashlib.md5()
        md5obj.update(f.read())
        _hash = md5obj.hexdigest()
        return str(_hash).lower()

def fetch_remote_data():
    meta_url = base_url + 'meta.json'
    resp = requests.get(meta_url)
    if resp.status_code == 200:
        return resp.json()
    else:
        return {}

def fetch_local_data():
    file_md5_dict = {}
    for dir_path, dir_names, filenames in os.walk(screensaver_path):
        for filename in filenames:
            if os.path.splitext(filename)[1] == '.png':
                file_path = os.path.join(screensaver_path, filename)
                file_md5_dict[filename] = get_file_md5(file_path)
    return file_md5_dict

def compare_local_remote(local_data, remote_data):
    local_unique_keys = local_data.keys() - remote_data.keys()
    remote_unique_keys = remote_data.keys() - local_data.keys()
    common_keys = local_data.keys() & remote_data.keys()
    diff_keys = []
    for key in common_keys:
        if local_data[key] != remote_data[key]:
            diff_keys.append(key)

    return local_unique_keys , remote_unique_keys , diff_keys

def process_local_unique(local_unique_keys):
    for key in local_unique_keys:
        file_path = '%s%s' % (screensaver_path, key)
        show_msg('remove ' + key)
        os.remove(file_path)

def process_remote_unique(remote_unique_keys):
    for key in remote_unique_keys:
        remote_file_url = '%sscreensavers/%s' % (base_url, key)
        file_path = '%s%s' % (screensaver_path, key)
        resp = requests.get(remote_file_url)
        show_msg('download ' + key)
        with open(file_path, 'wb') as f:
            f.write(resp.content)

def process_diff(diff_keys):
    process_local_unique(diff_keys)
    process_remote_unique(diff_keys)

def process():
    show_msg('process start')
    local_data = fetch_local_data()
    show_msg('local keys: %d' % len(local_data))
    remote_data = fetch_remote_data()
    if len(remote_data) == 0:
        show_msg('fetch_remote_data failed')
        return
    else:
        show_msg('remote keys: %d' % len(remote_data))
        local_unique_keys, remote_unique_keys, diff_keys = compare_local_remote(local_data, remote_data)
        show_msg('local unique keys: %d' % len(local_unique_keys))
        process_local_unique(local_unique_keys)
        show_msg('remote unique keys: %d' % len(remote_unique_keys))
        process_remote_unique(remote_unique_keys)
        show_msg('diff keys: %d' % len(diff_keys))
        process_diff(diff_keys)
        show_msg('process finished')

if __name__ == '__main__':
    process()
