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
"Settings"


from os import makedirs, name
from os.path import isdir, expanduser, join


class Config(dict):
    def __init__(self, filename):
        if name == "posix":
            self.path = expanduser("~/.config/TkC")
        elif name == "nt":
            if isdir(expanduser("~/Application Data")):
                self.path = expanduser("~/Application Data/TkC")
            else:
                self.path = expanduser("~/TkC")
        else:
            self.path = expanduser("~/TkC")
        if not isdir(self.path):
            makedirs(self.path)
        self.path = join(self.path, filename)
        cfgl = []
        try:
            with open(self.path) as fp:
                for line in iter(fp.readline, ""):
                    if not line.isspace():
                        nam, val = line.strip().split("=", 1)
                        cfgl.append((nam, eval(val)))
        except Exception:
            pass
        dict.__init__(self, cfgl)

    def save(self):
        with open(self.path, "w") as fp:
            for n, v in self.items():
                fp.write("%s=%s\n" % (n, repr(v)))
