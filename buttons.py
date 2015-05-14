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
"""
Callbacks for buttons
"""

from io_dialogs import AskCopy
from tkinter.messagebox import askyesno, showerror
from file_consts import *


def copy_button(cmdr):
    active, passive = cmdr.get_panels()
    names = active.get_selected_filenames()
    outdir = passive.pwd.get()
    if '..' in names:
        showerror('Spam', _("Parrent directory can not be copied"))
        return
    if len(names) == 1:
        msg = _("Copy file `%(file)s' to %(outdir)s?") % {'file': names[0],
                                                         'outdir': outdir}
    else:
        msg = _("Copy %(n)d files to %(outdir)s?") % {'n': len(names),
                                                     'outdir': outdir}
    dlg = AskCopy(
        cmdr.root, title=_("Copy"), message=msg, settings=cmdr.config)
    if not dlg.result:
        return
    names, errors = active.treater.expand_filenames(names)
    for name in names:
        try:
            print((name[FT_NAME]), name[FT_TYPE])
        except Exception:
            print(repr(name[FT_NAME]), name[FT_TYPE])
    print(len(names), errors, sum(i[1][6] for i in names))
