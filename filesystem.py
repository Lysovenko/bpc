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
"Nearest to GUI filesystem wrapper"

from stat import *
from file_consts import *
_filetypes = {S_IFREG: "regular", S_IFDIR: "directory", S_IFLNK: "link",
              S_IFIFO: "fifo", S_IFSOCK: "socket", S_IFBLK: "block",
              S_IFCHR: "character"}


class Filesystem:
    "Parrent class for virtual filesystems"

    def list_visible(self, visibility):
        result = []
        for file_name, file_stat, far_stat, mode in self.list_dir():
            if type(far_stat) is int:
                hidden = bool(far_stat & 2)
            else:
                hidden = file_name.startswith(".")
            st = far_stat if type(far_stat) is tuple else file_stat
            mode |= M_HIDDEN if hidden else 0
            mode |= M_SYMLINK if S_ISLNK(file_stat[ST_MODE]) else 0
            visible = True
            if hidden:
                visible = visibility.get("show_hidden_files", False)
            if file_name.endswith("~"):
                visible = visible and visibility.get(
                    "show_backup_files", False)
            if visible:
                file_type = _filetypes.get(S_IFMT(st[ST_MODE]))
                result.append((file_name, file_type, st[ST_SIZE],
                               st[ST_MTIME], mode))
        return result

    def list_dir(self, spath=None, single=False):
        "Dummy"
        return ()

    def expand_filenames(self, names, max_depth=10):
        rx_ok = X_OK | R_OK
        ex_names = []
        errors = []
        dir_stack = []
        layer = [i for i in self.list_dir() if i[0] in names]
        list_layers = [layer]
        while list_layers:
            layer = list_layers[-1]
            dir_stack_enlarged = False
            while layer:
                fname, file_st, far_st, uacc = layer.pop(-1)
                spath = tuple(dir_stack) + (fname,)
                if S_ISDIR(file_st[ST_MODE]):
                    if (uacc & rx_ok) == rx_ok:
                        ex_names.append((spath, file_st, far_st, uacc))
                        dir_stack.append(fname)
                        if len(dir_stack) > max_depth:
                            dir_stack.pop(-1)
                            errors.append((spath, 2))
                        else:
                            list_layers.append(self.list_dir(spath))
                            dir_stack_enlarged = True
                            break
                    else:
                        errors.append((spath, 1))
                else:
                    if uacc & R_OK:
                        ex_names.append((spath, file_st, far_st, uacc))
                    elif S_ISREG(file_st[ST_MODE]):
                        errors.append((spath, 1))
                    else:
                        errors.append((spath, 0))
            if dir_stack_enlarged:
                continue
            list_layers.pop(-1)
            if dir_stack:
                dir_stack.pop(-1)
        return ex_names, errors

    def files_check(self, files):
        """ Returns: True - folder unwriteable or
        List of errors (filename, error)
        error = 1 - file exists
        error = 2 can't write in principle """
        rwx_ok = W_OK | X_OK | R_OK
        f_info = self.list_dir(single=True)
        if (f_info[3] & rwx_ok) != rwx_ok:
            return True
        errors = []
        unaccessible_dirs = []
        for spath, fle_st, far_st, uacc in files:
            if any([spath[:len(i)] == i for i in unaccessible_dirs]):
                errors.append((name, 2))
            f_info = self.list_dir(spath, single=True)
            if f_info is not None:
                if S_ISDIR(f_info[1][ST_MODE]):
                    if not S_ISDIR(file_st[ST_MODE]):
                        errors.append((spath, 2))
                    elif (uacc & rwx_ok) != rwx_ok:
                        unaccessible_dirs.append(spath)
                else:
                    errors.append((spath, 1))
        # TODO: Treat sticky bits, owners an so on
        return errors
