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
"The Panel"

from operator import itemgetter
from tkinter import StringVar, PhotoImage, Frame
from tkinter.ttk import Label, Treeview, Scrollbar, Combobox
from os.path import dirname, join, pardir
from time import time, strftime, localtime
from placer import Placer
from file_consts import *


def autoscroll(sbar, first, last):
    """Hide and show scrollbar as needed."""
    first, last = float(first), float(last)
    if first <= 0 and last >= 1:
        sbar.grid_remove()
    else:
        sbar.grid()
    sbar.set(first, last)


class Panel:
    def __init__(self, frame, treater, settings):
        self.is_active = False
        self.oposite = lambda: None
        self.treater = treater
        self.placer = Placer()
        self.settings = settings
        self.sort_by = "name"
        self.sort_rev = False
        self.pwd = StringVar()
        self._places = None
        self.has_pardir = False
        self.pwd.set(self.treater.get_cur_dir())
        self.body(frame)
        ddir = join(dirname(__file__), "data")
        self.imgs = {}
        for t, f in (("directory", "folder.gif"), ("regular", "file.gif"),
                     ("link", "link.gif"), ("fifo", "fifo.gif"),
                     ("socket", "socket.gif"), ("block", "block.gif"),
                     ("character", "character.gif"),
                     ("Parent_dir", "pardir.gif")):
            self.imgs[t] = PhotoImage(master=frame, file=join(ddir, f))
        self.str_ids = {}
        self.id_range = []
        self.selected_ids = set()
        self.br_hist = []
        self.fresh()
        self.renheadings()

    def body(self, frame):
        "Place panel widgets"
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        top = Frame(frame)
        top.grid(column=0, row=0, sticky="ew")
        self.mounts = Combobox(top, takefocus=False, state="readonly")
        self.mounts["postcommand"] = self.get_places
        self.mounts.bind("<<ComboboxSelected>>", self.goto_place)
        self.mounts.pack(anchor="nw")
        pthl = Label(top, textvariable=self.pwd)
        pthl.pack(expand=True, anchor="w")
        self.tree = tree = Treeview(frame,
                                    columns=("size", "modified", "mode"))
        tree.grid(column=0, row=1, sticky="nwes")
        vsb = Scrollbar(frame, command=self.tree.yview, orient="vertical")
        vsb.grid(column=1, row=1, sticky="ns")
        tree["yscrollcommand"] = lambda f, l: autoscroll(vsb, f, l)
        hsb = Scrollbar(frame, command=self.tree.xview,
                        orient="horizontal")
        hsb.grid(column=0, row=2, sticky="ew")
        tree["xscrollcommand"] = lambda f, l: autoscroll(hsb, f, l)
        tree.column("size", width=70, anchor="center")
        tree.column("modified", width=70, anchor="center")
        tree.column("mode", width=70, anchor="center")
        tree.heading("#0", command=lambda: self.on_heading("name"))
        tree.heading("size", command=lambda: self.on_heading("size"))
        tree.heading("modified", command=lambda: self.on_heading("date"))
        tree.tag_configure("selected", foreground="red")
        for i in (("<Return>", self.enter_file),
                  ("<Double-Button-1>", self.enter_file),
                  ("<Right>", self.enter_file), ("<Left>", self.go_back),
                  ("<Tab>", self.switch), ("<Home>", self.go_top),
                  ("<Button-1>", self.activate),
                  ("<Insert>", self.turn_selection),
                  ("<Control-r>", self.refresh)):
            tree.bind(*i)

    def renheadings(self):
        "Rename headings due to new sorting conditions"
        arrow_up = " \u2191"
        arrow_down = " \u2193"
        for col, name, sb in (
                ("#0", _("Name"), "name"),
                ("size", _("Size"), "size"), ("modified", _("Date"), "date"),
                ("mode", _("Attr."), None)):
            if self.sort_by == sb:
                name += arrow_down if self.sort_rev else arrow_up
            self.tree.heading(col, text=name)

    def on_heading(self, name):
        "An heading was clicked"
        if self.sort_by == name:
            self.sort_rev = not self.sort_rev
        else:
            self.sort_by = name
            self.sort_rev = False
        self.sort_tree()
        self.renheadings()

    def fresh(self):
        "Update tree items. Returns True on error."
        files = self.treater.list_visible(self.settings)
        if files is None:
            return True
        self.clear()
        self.has_pardir = self.treater.has_pardir()
        if self.has_pardir:
            self.tree.insert("", "end", "Parent_dir", text=pardir,
                             image=self.imgs["Parent_dir"])
        ltp = localtime(time())
        for name, ft, sz, mt, mode in files:
            mt = localtime(mt)
            if ltp.tm_year > mt.tm_year:
                smt = strftime("%b %Y", mt)
            elif ltp.tm_yday > mt.tm_yday:
                smt = strftime("%d %b", mt)
            else:
                smt = strftime("%H:%M")
            if sz < 1024:
                ssz = sz
            elif sz < 1048576:
                ssz = "%dK" % (sz // 1024)
            else:
                ssz = "%dM" % (sz // 1048576)
            mod_arr = []
            # NOTE: Mentions of letters are: X - execute, W - write, R - read,
            # H - hidden, S - symbolic link
            for i, l in enumerate(_("XWRHS")):
                mod_arr.append(l if mode & (1 << i) else "-")
            mod_arr.reverse()
            mds = "".join(mod_arr)
            iid = self.tree.insert("", "end", text=name,
                                   values=(ssz, smt, mds),
                                   image=self.imgs[ft])
            self.str_ids[iid] = (name, ft, sz, mt, mode)
            self.id_range.append(iid)
        self.sort_tree()

    def clear(self):
        for i in reversed(self.id_range):
            self.tree.delete(i)
        if self.has_pardir:
            self.tree.delete("Parent_dir")
        self.str_ids.clear()
        self.selected_ids.clear()
        del self.id_range[:]

    def sort_tree(self):
        si = {"name": 0, "size": 2, "date": 3}[self.sort_by]
        sd = self.str_ids
        key = lambda x: sd[x][si]
        self.id_range.sort(key=key, reverse=self.sort_rev)
        key = lambda x: 2 if sd[x][1] != "directory" else 1
        self.id_range.sort(key=key)
        mv = self.tree.move
        start = 1 if self.has_pardir else 0
        for pos, iid in enumerate(self.id_range, start):
            mv(iid, "", pos)

    def enter_file(self, evt=None):
        iid = self.tree.focus()
        if iid == "Parent_dir":
            self._change_dir(pardir)
            return
        if self.str_ids[iid][FT_TYPE] == "directory":
            mode = self.str_ids[iid][FT_MODE]
            mask = M_READABLE | M_EXECUTABLE
            if mode & mask != mask:
                return
            self._change_dir(self.str_ids[iid][FT_NAME])

    def turn_selection(self, evt=None):
        iid = self.tree.focus()
        if iid != "Parent_dir":
            selected = self.selected_ids
            if iid in selected:
                self.tree.item(iid, tags=())
                selected.discard(iid)
            else:
                selected.add(iid)
                self.tree.item(iid, tags=("selected"))
        if self.settings.get("insert_moves_down", True) and self.id_range:
            if iid == "Parent_dir":
                move_to = 0
            else:
                move_to = self.id_range.index(iid) + 1
                if move_to >= len(self.id_range):
                    move_to = -1
            tree = self.tree
            tree.focus(item=self.id_range[move_to])
            tree.selection_remove(*(tree.selection()))
            tree.selection_add(tree.focus())

    def go_back(self, evt=None):
        try:
            prdir = self.br_hist.pop(-1)
        except IndexError:
            return
        self._change_dir(prdir, False)

    def refresh(self, evt=None):
        iid = self.tree.focus()
        fid = self.str_ids
        fn = fid[iid][0]
        pos = self.id_range.index(iid)
        self.fresh()
        iid = ""
        for i in fid:
            if fid[i][0] == fn:
                iid = i
                break
        if iid == "":
            if pos < len(self.id_range):
                iid = self.id_range[pos]
            else:
                iid = self.id_range[-1]
        self.tree.focus(item=iid)
        self.activate()

    def activate(self, evt=None):
        if self.tree.focus() == "":
            self.tree.focus(item=self.id_range[0])
        self.tree.selection_add(self.tree.focus())
        oposite = self.oposite()
        if oposite is not None:
            opt = oposite.tree
            sel = opt.selection()
            if sel:
                opt.selection_remove(*sel)
            oposite.is_active = False
        self.tree.focus_set()
        self.is_active = True

    def switch(self, evt=None):
        if self.oposite() is None:
            return
        self.oposite().activate()

    def go_top(self, evt=None):
        self.tree.focus(item=self.id_range[0])
        sel = self.tree.selection()
        if sel:
            self.tree.selection_remove(*sel)
        self.tree.selection_add(self.id_range[0])

    def get_places(self):
        try:
            places = self.placer.placing_items()
        except AttributeError:
            self._places = None
            self.mounts["values"] = None
            return
        self.mounts["values"] = [i[0] for i in places]
        # self.mounts["values"] can be changet after assignment. Therefore
        # it is more safe to replace names of mount points by changed ones.
        self._places = dict((j, i[1]) for i, j in
                            zip(places, self.mounts["values"]))

    def goto_place(self, evt=None):
        if self._places is None:
            return
        place = self._places[self.mounts.get()]
        self._change_dir(place)

    def _change_dir(self, path, remember=True):
        previous = self.treater.get_cur_dir()
        if self.treater.cd(path):
            return
        if self.fresh():
            self.treater.cd(previous)
        elif remember:
            self.br_hist.append(previous)
        self.pwd.set(self.treater.get_cur_dir())
        self.activate()

    def get_selected_filenames(self):
        result = []
        if not self.selected_ids:
            iid = self.tree.focus()
            if iid != "Parent_dir":
                result.append(self.str_ids[iid][FT_NAME])
        for iid in self.selected_ids:
            result.append(self.str_ids[iid][FT_NAME])
        return result
