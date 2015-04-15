# Copyright 2015 Serhiy Lysovenko
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Local filesystem operations"""

from os import listdir, stat, lstat, curdir, chdir, name, access, F_OK,\
    mkdir
from os.path import realpath, normpath, join, split, pardir, islink,\
    expanduser, isdir, exists, sep
from stat import S_IFMT, S_IFSOCK, S_IFLNK, S_IFREG, S_IFBLK, \
    S_IFDIR, S_IFCHR, S_IFIFO
from filesystem import Filesystem
from file_consts import *
_filetypes = (('regular', S_IFREG), ('directory', S_IFDIR), ('link', S_IFLNK),
              ('fifo', S_IFIFO), ('socket', S_IFSOCK), ('block', S_IFBLK),
              ('character', S_IFCHR))
if name == 'nt':
    from ctypes import windll
# XXX prevent I/O operations
from test.pseudofile import open
mkdir = lambda x, y=0: None


class Local_fs(Filesystem):
    def __init__(self, path=curdir):
        self.__pwd = realpath(path)

    def cd(self, path):
        new_dir = normpath(join(self.__pwd, path))
        try:
            chdir(new_dir)
        except OSError:
            return True
        self.__pwd = new_dir

    def cd_pardir(self):
        self.cd(pardir)

    def has_pardir(self):
        return bool(split(self.__pwd)[1])

    def get_cur_dir(self):
        return self.__pwd

    def list_dir(self, spath=None, single=False):
        if single:
            if spath is None:
                path, filename = split(self.__pwd)
            else:
                path = join(self.__pwd, *(spath[:-1]))
                filename = spath[-1]
        else:
            path = join(self.__pwd, *spath) if spath else self.__pwd
        try:
            chdir(path)
        except OSError:
            return None
        if single:
            lst = [filename]
        else:
            lst = listdir(curdir)
        res = []
        for file_name in lst:
            try:
                file_st = tuple(lstat(file_name))
            except OSError:
                continue
            if name == 'nt' and file_st:
                far_st = windll.kernel32.GetFileAttributesW(file_name)
            elif islink(file_name):
                try:
                    far_st = tuple(stat(file_name))
                except OSError:
                    far_st = None
            else:
                far_st = file_st
            usr_acc = 0
            for i in range(3):
                if access(file_name, 1 << i):
                    usr_acc |= 1 << i
            res.append((file_name, file_st, far_st, usr_acc))
        if single:
            res = res[0] if res else None
        return res

    def open(self, spath, mode='wb'):
        "Obtaining File like object, opened in binary mode for write"
        chdir(self.__pwd)
        if mode == 'wb':
            for i in range(1, len(spath)):
                pth = join(*spath[:i])
                if isdir(pth):
                    continue
                if isfile(pth):
                    remove(pth)
                mkdir(pth)
        # in this case file-like object is common File object,
        # but in all other treaters it will be not working
        return open(name, mode)
