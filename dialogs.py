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
""" """
# from tkinter.simpledialog import Dialog
from tkinter.ttk import Button, Checkbutton, Separator
# Label, Entry,
from tkinter import IntVar, Toplevel, Frame


class Dialog(Toplevel):
    "Base class for custom dialogs"
    def __init__(self, parent, title=None, **user_params):
        self.had_focus = parent.focus_get() if parent is not None else None
        Toplevel.__init__(self, parent)
        if title:
            self.title(title)
        self.result = None
        body = Frame(self)
        self.initial_focus = self.body(body, **user_params)
        body.pack(padx=5, pady=5)
        # ASSUME: gettext module is activated
        self.btn_ok_text = _("OK")
        self.btn_cancel_text = _("Cancel")
        self.button_box()
        if not self.initial_focus:
            self.initial_focus = self
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        # TOTDO: Make correct dialog displacement
        self.initial_focus.focus_set()
        self.grab_set()
        self.wait_window(self)

    def body(self, master):
        """
        Dummy method for overriding which have to create the dialog body.
        Returns the widget which should have initial focus or None.
        Also you can override here the members btn_ok_text="OK" and
        btn_cancel_text="Cancel" to change buttons titles in button box
        """
        return

    def button_box(self):
        separ = Separator(self, orient='horizontal')
        separ.pack(expand=1, fill='x')
        box = Frame(self)
        b = Button(box, text=self.btn_ok_text, width=10,
                   command=self.accept, default='active')
        b.pack(side='left', padx=5, pady=5)
        b = Button(box, text=self.btn_cancel_text, width=10,
                   command=self.destroy)
        b.pack(side='right', padx=5, pady=5)
        self.bind("<Return>", self.accept)
        self.bind("<Escape>", self.destroy)
        box.pack()

    def accept(self, event=None):
        "Event for OK button"
        errorneous = self.validate()
        if errorneous is not None:
            errorneous.focus_set()
            return
        self.withdraw()
        self.update_idletasks()
        try:
            self.apply()
        finally:
            self.destroy()

    def destroy(self, event=None):
        "Put the focus back to the parent window and destroy the dialod"
        if self.had_focus is not None:
            self.had_focus.focus_set()
        Toplevel.destroy(self)

    def validate(self):
        """
        Dummy method for overriding which have to validate the data.
        Returns the widget which contain errorneous data or None.
        """
        return None

    def apply(self):
        '''process the data
        This method is called automatically to process the data, *after*
        the dialog is destroyed. By default, it does nothing.
        '''
        pass


class Dlg_panset(Dialog):
    def __init__(self, parent, cfg):
        self.config = cfg
        self.is_hidden = IntVar()
        self.is_hidden.set(cfg.get('show_hidden_files', 0))
        self.is_backup = IntVar()
        self.is_backup.set(cfg.get('show_backup_files', 0))
        Dialog.__init__(self, parent, title="Panel settings")

    def body(self, master):
        "place user dialog widgets"
        chk1 = Checkbutton(master, text='Show hidden files',
                           variable=self.is_hidden)
        chk1.pack()
        chk2 = Checkbutton(master, text='Show backup files',
                           variable=self.is_backup)
        chk2.pack()
        self.resizable(width=0, height=0)
        return chk1

    def apply(self):
        "On ok button pressed"
        self.config['show_hidden_files'] = self.is_hidden.get()
        self.config['show_backup_files'] = self.is_backup.get()


if __name__ == '__main__':
    from tkinter import Tk, Button
    root = Tk()
    Button(root, text="Hello!").pack()
    root.update()
    d = Dlg_panset(root, {})
    # root.wait_window(d)
