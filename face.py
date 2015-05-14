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
Making a face of the application
"""

from tkinter import Tk, Menu, PhotoImage
from tkinter.ttk import Panedwindow, Frame, Sizegrip, Button
from os.path import dirname, join, isdir
from local_fs import Local_fs
from weakref import ref
from panel import Panel
from settings import Config
from file_consts import *
import buttons


class Face:
    def __init__(self, root):
        self.config = Config('tkc.ini')
        root.title('Tkinter Commander')
        root.protocol("WM_DELETE_WINDOW", self.on_delete)
        self.root = root
        root.geometry(self.config.get('fm_geometry'))
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)
        pw = Panedwindow(root, orient='horizontal', takefocus=False)
        frame = Frame(pw)
        self.left = Panel(frame, Local_fs(), self.config)
        pw.add(frame)
        pw.pane(frame, weight=1)
        frame = Frame(pw)
        self.right = Panel(frame, Local_fs(), self.config)
        self.right.oposite = ref(self.left)
        self.left.oposite = ref(self.right)
        self.left.activate()
        pw.add(frame)
        pw.pane(frame, weight=1)
        pw.grid(column=0, row=1, columnspan=2, sticky='senw')
        self.add_menu()
        self.add_btns()
        root.tk.call(
            'wm', 'iconphoto', root._w,
            PhotoImage(file=join(dirname(__file__), 'data', 'favicon.gif')))

    def add_menu(self):
        top = self.root
        top['menu'] = menubar = Menu(top)
        menu_file = Menu(menubar)
        menu_settings = Menu(menubar)
        menu_help = Menu(menubar)
        menubar.add_cascade(menu=menu_file, label=_('File'))
        menubar.add_cascade(menu=menu_settings, label=_('Settings'))
        menubar.add_cascade(menu=menu_help, label=_('Help'))
        menu_settings.add_command(label=_('Pannel Settings'),
                                  command=self.dlg_panset)

    def add_btns(self):
        root = self.root
        frame = Frame(root)
        for key, text, command in (
                (3, _("F3 View"), self.on_F3),
                (4, _("F4 Edit"), self.on_F4), (5, _("F5 Copy"), self.on_F5),
                (6, _("F6 Move"),  self.on_F6),
                (7, _("F7 Make Directory"), self.on_F7),
                (8, _("F8 Remove"), self.on_F8),
                (10, _("F10 Exit"), self.on_F10)):
            btn = Button(frame, text=text, command=command, takefocus=False)
            btn.pack(side='left', fill='x', expand=True)
            root.bind_all('<F%d>' % key, func=command)
        sz = Sizegrip(frame)
        sz.pack(side='right', anchor='se')
        frame.grid(column=0, row=2, columnspan=2, sticky='we')

    def get_panels(self):
        "returns (active, passive) panels"
        if self.left.is_active:
            return self.left, self.right
        return self.right, self.left

    def on_delete(self):
        self.config['fm_geometry'] = self.root.geometry()
        self.config.save()
        self.root.destroy()

    def on_F3(self, evt=None):
        print('F3')

    def on_F4(self, evt=None):
        print('F4')

    def on_F5(self, evt=None):
        buttons.copy_button(self)

    def on_F6(self, evt=None):
        print('F6')

    def on_F7(self, evt=None):
        print('F7')

    def on_F8(self, evt=None):
        print('F8')

    def on_F10(self, evt=None):
        self.on_delete()

    def dlg_panset(self):
        from dialogs import Dlg_panset
        Dlg_panset(self.root, self.config)


def start_face():
    try:
        import gettext
    except ImportError:
        __builtins__.__dict__['_'] = str
    else:
        localedir = join(dirname(__file__), 'i18n', 'locale')
        if isdir(localedir):
            gettext.install('TkC', localedir=localedir)
        else:
            gettext.install('TkC')
    root = Tk(className='commander')
    Face(root)
    root.mainloop()


if __name__ == '__main__':
    start_face()
