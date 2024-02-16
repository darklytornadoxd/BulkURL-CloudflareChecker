### === Project Name: Bulk URL Validator & Cloudflare Checker === ###
### === Author: https://github.com/darklytornadoxd === ###

import os
import platform
import subprocess
import requests
import threading
from queue import Queue
import time
from requests.exceptions import ConnectionError

time.sleep(1)

def clear_screen():
    current_os = platform.system()
    
    command = 'cls' if current_os == 'Windows' else 'clear'
    
    if current_os == 'Windows':
        os.system(command)
    else:
        subprocess.run(['clear'])

clear_screen()

def is_using_cloudflare(headers):
    return 'cf-ray' in headers

def worker():
    while True:
        url = q.get()
        # Ensure the URL has a scheme
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        try:
            response = requests.get(url, timeout=10)
            cloudflare = 'Yes' if is_using_cloudflare(response.headers) else 'No'
            valid = 'Yes' if response.status_code == 200 else 'No'
            result = f"Link: {url} | Valid: {valid} | Cloudflare: {cloudflare}\n"
        except ConnectionError as e:
            result = f"Link: {url} | Valid: No | Cloudflare: No | Error: DNS resolution failed\n"
        except requests.RequestException as e:
            result = f"Link: {url} | Valid: No | Cloudflare: No | Error: {e}\n"
        finally:
            print(result)
            with lock:
                with open('results.txt', 'a') as f:
                    f.write(result)
            q.task_done()

if not os.path.exists('links.txt'):
    print('The file named links.txt is not able to be opened, or it does not exist. Make sure the file is a valid text file, or ensure that it is not corrupt or missing.')
else:
    num_threads = int(input("Specify a number of threads to use: "))

    q = Queue()
    lock = threading.Lock()

    with open('links.txt', 'r') as f:
        for line in f:
            q.put(line.strip())

    for i in range(num_threads):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()

    q.join()

    time.sleep(1)
    exit()