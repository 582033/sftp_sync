#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import os
import re
import sys
import pyinotify
import pysftp
from ftplib import FTP

sourcePath = '/var/www/html/cms/uploadfile/'
sftpIp = '127.0.0.1'
sftpUser = 'foo'
sftpPwd = 'bar'
sftpPort = 22234

class ftp():
    def __init__(self, host, user, pwd, pt):
        self.ftp = FTP_TLS()
        self.ftp.connect(host, pt)
        self.ftp.login(user, pwd)
        self.ftp.port_p()
        self.ftp.retrlines('LIST')

    #检查是否为文件夹,并进行sftp.put
    def loop_mkdir(self, target):
        #检查tmp_target是否为目录
        print "target:  %s" % (target)
        print "pwd:  %s" % (self.ftp.pwd)
        if(os.path.isdir(target)):
            if not self.ftp.exists(target):
                self.ftp.mkd(target)
        else:
            if(len(target.split('/')) > 1):
                self.sftp.put(target, remotepath=target, preserve_mtime=True)
            else:
                self.sftp.put(target, preserve_mtime=True)



class sftp():
    def __init__(self, host, user, pwd, pt):
        self.sftp = pysftp.Connection(host, username = user, password = pwd, port = pt)

    #检查是否为文件夹,并进行sftp.put
    def loop_mkdir(self, target):
        #检查tmp_target是否为目录
        print "target:  %s" % (target)
        print "pwd:  %s" % (self.sftp.pwd)
        if(os.path.isdir(target)):
            if not self.sftp.exists(target):
                self.sftp.mkdir(target)
        else:
            if(len(target.split('/')) > 1):
                self.sftp.put(target, remotepath=target, preserve_mtime=True)
            else:
                self.sftp.put(target, preserve_mtime=True)

    def rm(self, src):
        relativePath = re.sub(sourcePath, '', src)
        if os.path.isfile(src):
            if(self.sftp.exists(relativePath)):
                self.sftp.remove(relativePath)
        #else:
        #    print relativePath
        #    if(self.sftp.exists(relativePath):
        #        self.sftp.rmdir(relativePath)


    def put(self, src):
        relativePath = re.sub(sourcePath, '', src)
        #sftp.put_r(sourcePath, targetPath, preserve_mtime=True)
        plist = relativePath.split('/')
        while '' in plist:
            plist.remove('')
        #删除最后的'/'
        #print plist

        tmp_target = sourcePath

        for target in plist:
            tmp_target = "%s/%s" % (tmp_target, target)
            tmp_target = re.sub('/{2,}', '/', tmp_target)
            relativePath = re.sub(sourcePath, '', tmp_target)
            self.loop_mkdir(relativePath)

    def __del__(self):
        self.sftp.close()



class EventHandler(pyinotify.ProcessEvent):
    def __init__(self):
        self.sftp = sftp(sftpIp, sftpUser, sftpPwd, sftpPort)

    def process_IN_CREATE(self, event):
        print "create %s" % event.pathname
        self.sftp.put(event.pathname)

    def process_IN_DELETE(self, event):
        print "delete %s" % event.pathname
        self.sftp.rm(event.pathname)

    def process_IN_MODIFY(self, event):
        print "modify %s" % event.pathname
        self.sftp.put(event.pathname)


def realtime():
    #todo 原文件首次传输
    wm = pyinotify.WatchManager()
    notifier = pyinotify.Notifier(wm, EventHandler())
    wm.add_watch(sourcePath, pyinotify.ALL_EVENTS, rec=True, auto_add=True)    #rec=True sub-dir support
    notifier.loop()

def repush():
    print "foo"

#删除文件夹时异常退出,暂时禁止删除文件夹
if __name__ == "__main__":
    #if(len(sys.argv) != 2 or sys.argv[1] != 'realtime'):
    #    print u"\n 参数错误\n %s  realtime 实时监控提交新增或修改的文件" % (sys.argv[0])
    #else:
    #    if(sys.argv[1] == 'realtime'):
    #        realtime()
    realtime()
