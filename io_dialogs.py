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
"""Dialogs for copyng, movind, making a directory"""

from dialogs import Dialog
from tkinter.ttk import Label, Progressbar


class AskCopy(Dialog):
    def body(self, master, message="", settings={}):
        self.settings = settings
        lab = Label(master, text=message)
        lab.pack()

    def apply(self):
        self.result = True


class CopyMoveProgres(Dialog):
    def body(self, master, active=None, passive=None, remove=False):
        # progressbars and dong progress
        pass
