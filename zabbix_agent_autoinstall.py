#!/usr/bin/python
# -*- coding: utf-8 -*-

#######################################################
# zabbix_agent_autoinstall.py v0.1 script for automatic installation zabbix-agent v4.4
# Maxim Sasov  maksim.sasov@hoster.by 08/04/2020
#######################################################


import platform
import os,sys
import socket
import os.path
import shutil
from shutil import copyfile
import re
import subprocess

global centos_zabbix_repository, verdist, dist_linux

# config for zabbix server
Server = '95.47.99.52'
ServerActive = '95.47.99.52'
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)


support_dist = ['centos 8','centos 7','centos 6','centos 5','debian 10', 'debian 9','debian 8', 'Ubuntu 18','Ubuntu 16','Ubuntu 14']
centos_zabbix_repository = {'centos 8':'https://repo.zabbix.com/zabbix/4.4/rhel/8/x86_64/zabbix-release-4.4-1.el8.noarch.rpm',
                            'centos 7':'https://repo.zabbix.com/zabbix/4.4/rhel/7/x86_64/zabbix-release-4.4-1.el7.noarch.rpm',
                            'centos 6':'https://repo.zabbix.com/zabbix/4.4/rhel/6/x86_64/zabbix-release-4.4-1.el6.noarch.rpm',
                            'centos 5':'https://repo.zabbix.com/zabbix/4.4/rhel/5/x86_64/zabbix-release-4.4-1.el5.noarch.rpm'}

debian_ubuntu_zabbix_repository = {'debian 10':'https://repo.zabbix.com/zabbix/4.4/debian/pool/main/z/zabbix-release/zabbix-release_4.4-1+buster_all.deb',
                                    'debian 9':'https://repo.zabbix.com/zabbix/4.4/debian/pool/main/z/zabbix-release/zabbix-release_4.4-1+stretch_all.deb',
                                    'debian 8':'https://repo.zabbix.com/zabbix/4.4/debian/pool/main/z/zabbix-release/zabbix-release_4.4-1+jessie_all.deb',
                                    'Ubuntu 18':'https://repo.zabbix.com/zabbix/4.4/ubuntu/pool/main/z/zabbix-release/zabbix-release_4.4-1+bionic_all.deb',
                                    'Ubuntu 16':'https://repo.zabbix.com/zabbix/4.4/ubuntu/pool/main/z/zabbix-release/zabbix-release_4.4-1+xenial_all.deb',
                                    'Ubuntu 14':'https://repo.zabbix.com/zabbix/4.4/ubuntu/pool/main/z/zabbix-release/zabbix-release_4.4-1+trusty_all.deb'}

dist_linux = list(platform.dist())
match =  re.findall(r'^\d{0,2}', dist_linux[1])
verdist = dist_linux[0] + ' ' + match[0]


def zabbix_conf():
    if os.path.exists('/etc/zabbix/zabbix_agentd.conf'):
        shutil.copy('/etc/zabbix/zabbix_agentd.conf', '/etc/zabbix/zabbix_agentd.conf_orig_bak')
        f = open (os.path.abspath(r"/etc/zabbix/zabbix_agentd.conf") , "r+" )
        config = f.read()
        config = re.sub(r'# SourceIP=','SourceIP=%s'%(host_ip), config)
        config = re.sub(r'Server=127.0.0.1','Server=%s'%(Server), config)
        config = re.sub(r'ServerActive=127.0.0.1','ServerActive=%s'%(ServerActive), config)
        config = re.sub(r'Hostname=Zabbix server','Hostname=%s'%(host_name), config)
        config = re.sub(r'# HostMetadata=','HostMetadata=%s'%(HostMetada), config)
        f.seek(0)
        f.write(config)
        f.truncate()
        f.close()
    else:
        print("\033[91mzabbix_agentd.conf not found!\033[0m")
    command = ['service', 'zabbix-agent', 'start']
    p = subprocess.Popen(command)
    p.wait()
    if p.returncode != 0:
        print("Something went wrong")
def autoinstall_zabbix_agent():
    if dist_linux[0] == 'centos':
        print '\033[92mStart install zabbix-agent v4.4 on %s\033[0m'%(verdist)
        rpm = centos_zabbix_repository.get(verdist)
        command = ['rpm','-Uvh', rpm]
        p = subprocess.Popen(command)
        p.wait()
        if p.returncode != 0:
            print("Something went wrong")
        command = ['yum', '-y', 'install', 'zabbix-agent']
        p = subprocess.Popen(command)
        p.wait()
        if p.returncode != 0:
            print("Something went wrong")
    elif (dist_linux[0] == 'debian') or (dist_linux[0] == 'Ubuntu'):
         print '\033[92mStart install zabbix-agent v4.4 on  %s\033[0m'%(verdist)
         rpm = debian_ubuntu_zabbix_repository.get(verdist)
         deb = re.findall(r'zabbix-release_4\.4-1\+\w+\.deb', rpm)
         command1 = ['wget', rpm]
         command2 = ['dpkg', '-i', deb[0]]
         command3 = ['apt', 'update']
         command4 = ['apt', '-y', 'install', 'zabbix-agent']
         command5 = ['rm', '-f', deb[0]]
         cmd = [command1,command2,command3,command4,command5]
         for i in cmd:
             p = subprocess.Popen(i)
             p.wait()
             if p.returncode != 0:
                 print("Something went wrong")
    zabbix_conf()

def check_dict():
    if verdist in support_dist:
        autoinstall_zabbix_agent()
    else:
        print verdist,' \033[91mnot support\033[0m'


try:
    HostMetada = sys.argv[1]
    if not os.path.exists('/usr/sbin/zabbix_agentd'):
        check_dict()
    else:
        print("\033[91mFound installed zabbix-agent\033[0m (please check command '\033[96mzabbix_agentd -V\033[0m')")
except IndexError:
    print("\033[91mRequired parameter\033[0m '\033[93mtest_hoster\033[0m' \033[91mor\033[0m '\033[93madmin_hoster\033[0m'  \033[91mnot found\033[0m  (command example: \033[96m./zabbix_agent_autoinstall.py test_hoster\033[0m)")
    sys.exit (1)
