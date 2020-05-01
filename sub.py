# coding: utf-8
import subprocess
import os
import re
import time
import simplejson
import argparse


# path_info-------------------------
gobuster_path = r' '
chrome_path = r' '
crawlergo_path = r' '
httprobe_path = r' '
dictionary_path_default = r'3000.txt'
save_dir_name = ''
# list
entrance_list = []
subdomain_list = []


def parse_args():
    usage = '''
    sub.py [-h]
    sub.py -d <domain>   -u <url>  [-w <dictionary_path>]  [-o <dirname>]
    sub.py -f <submain_file_path>   [-o <dirname>]
    '''
    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument('-u', '--url', help='input url to crawlergo', type=str)
    parser.add_argument('-d', '--domain', help='input domain to burst', type=str)
    parser.add_argument('-w', '--dictionary', help='input dictionary to burst, default is 3000.txt', type=str, default=dictionary_path_default)
    parser.add_argument('-f', '--file', help='input your subdomain file to verify', type=str)
    parser.add_argument('-o', '--dirname', help='input dirname to save result, default is time ', type=str)
    return parser.parse_args()


def path_is_true():
    for i in [gobuster_path, dictionary_path_default, chrome_path, crawlergo_path, httprobe_path]:
        if not os.path.exists(i):
            print(f'[error!!!]  {i}  have  error,  Please  enter  the  correct  path.')


def do_gobuster(domain, dictionary_path):
    global subdomain_list
    cmd = [gobuster_path, "dns", "-t", "30", "-w", dictionary_path, "-q", "–wildcard", "-d", domain]
    gobuster_result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    get, error = gobuster_result.communicate()
    result = get.decode('utf-8')
    pattern = r'Found: (.*?)\n'
    domain_list_go = re.findall(pattern, result)
    subdomain_list.extend(domain_list_go)
    print('[+] gobuster get  %s  subdomain.' % len(domain_list_go))


def do_crawlergo(url):
    global subdomain_list
    global entrance_list
    cmd = [crawlergo_path, "-c", chrome_path, "-t", "10", "-f", "smart", "--fuzz-path", "--output-mode", "json", url]
    crawlergo_result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    get, error = crawlergo_result.communicate()
    result = simplejson.loads(get.decode().split("--[Mission Complete]--")[1])
    domain_list_craw = result["sub_domain_list"]
    entrance_url = result["req_list"]
    if len(domain_list_craw) == 1:
        print('[-] crawlergo  is  not  work,  Check url')
    else:
        print('[+] crawlergo  get  %i  subdomain' % len(domain_list_craw))
        subdomain_list.extend(domain_list_craw)
        for i in entrance_url:
            entrance = i['url'] + '  method:'+i['method']
            entrance_list.append(entrance)
        print('[+] crawlergo get %i entrance_url with http_method' % len(entrance_list))


def save_name():
    global save_dir_name
    if args.dirname:
        try:
            os.mkdir(args.dirname)
            dir_name = args.dirname
        except FileExistsError:
            os.mkdir(time.strftime("%m-%d-%H-%M-%S", time.localtime()))
            dir_name = time.strftime("%m-%d-%H-%M-%S", time.localtime())
    else:
        os.mkdir(time.strftime("%m-%d-%H-%M-%S", time.localtime()))
        dir_name = time.strftime("%m-%d-%H-%M-%S", time.localtime())
    save_dir_name = os.path.join(os.getcwd(), dir_name)


def save(file_name, list_name, info):
    save_path = os.path.join(save_dir_name, file_name)
    with open(save_path, 'w+', encoding='utf-8') as f_obj:
        for i in list_name:
            f_obj.write(i+'\n')
    print('[+] %i  %s  Has been  saved  in %s' % (len(list_name), info, save_path))


def do_httprobe(option):
    if option == 1:
        path = os.path.join(save_dir_name, 'subdomain_exist.txt')
    else:
        path = args.file
    if os.name == 'nt':
        httprobe_result = os.popen(f'type {path} | {httprobe_path}').read()
    elif os.name == 'posix':
        httprobe_result = os.popen(f'cat {path} | {httprobe_path}').read()
    else:
        print('[-] Unable to identify operating system')
    save_path = os.path.join(save_dir_name, 'subdomain_alive.txt')
    with open(save_path, 'w+', encoding='utf-8') as file_obj:
        file_obj.write(httprobe_result)
        file_name = file_obj.name
    print('[+] alive  subdomain  is  saved  in  %s' % file_name)


def do_webscreenshot():
    path = os.path.join(save_dir_name, 'subdomain_alive.txt')
    save_path = os.path.join(save_dir_name, 'img')
    os.popen(f'webscreenshot -i {path} -o{save_path} -w 20 -m ').read()
    print(f'[+] screenshots is  saved  in  img ')


def main():
    global subdomain_list
    if args.url and args.domain:
        if args.dictionary:
            do_gobuster(args.domain, args.dictionary)
        else:
            do_gobuster(args.domain, dictionary_path_default)
        do_crawlergo(args.url)
        subdomain_list = list(set(subdomain_list))
        print('[info] remove duplication, get %i subdomain' % (len(subdomain_list)))
        save_name()
        save('subdomain_exist.txt', subdomain_list, 'subdomain')
        save('path.txt', entrance_list, 'entrance_url')
        do_httprobe(option=1)
        do_webscreenshot()
    elif args.file:
        if not os.path.exists(args.file):
            print(f'[error]  {args.file} have  error,  Please  enter  the  correct domain file  path.')
        else:
            save_name()
            do_httprobe(option=2)
            do_webscreenshot()
    else:
        print('sub.py -h')


if __name__ == '__main__':
    print(r'''
                   ___                                       __      
 __              / ___\                                     /\ \__   
/\ \     ___    /\ \__/   ___                __        __   \ \  _\  
\ \ \  /  _  \  \ \  __\ / __`\            / _  \    / __ \  \ \ \/  
 \ \ \ /\ \/\ \  \ \ \_//\ \L\ \          /\ \L\ \  /\  __/   \ \ \_ 
  \ \_\\ \_\ \_\  \ \_\ \ \____/          \ \____ \ \ \____\   \ \__\
   \/_/ \/_/\/_/   \/_/  \/___/   _______  \/___L\ \ \/____/    \/__/
                                 /\______\   /\____/                 
                                 \/______/   \_/__/                  
    ''')
    path_is_true()
    args = parse_args()
    main()
