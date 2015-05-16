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
"Search for places"

from os import name, listdir
from os.path import expanduser, isdir, realpath, join
if name == "nt":
    from ctypes import windll
    from string import ascii_uppercase


class Placer:
    def __init__(self):
        if name == "posix":
            self.__system_places = self.__posix_places
        elif name == "nt":
            self.__system_places = self.__nt_places

    def placing_items(self):
        "Disks, mountpoints etc"
        os_name = name
        result = [("Home", expanduser("~"))]
        result += self.__system_places()
        return result

    def __posix_places(self):
        result = []
        labels = {}
        titles = {}
        by_label = "/dev/disk/by-label"
        if isdir(by_label):
            for label in listdir(by_label):
                labels[realpath(join(by_label, label))] = label
        with open("/proc/mounts") as fp:
            for line in fp:
                device, path, dummy = line.split(" ", 2)
                if "/" not in device:
                    continue
                spl = path.split("\\")
                path = spl[0]
                for i in spl[1:]:
                    path += chr(int(i[:3], 8)) + i[3:]
                if device.startswith("/"):
                    device = realpath(device)
                    device = labels.get(device, device)
                times = titles.get(device, 0)
                if times:
                    title = "(%d) %s" % (times + 1, device)
                else:
                    title = device
                titles[device] = times + 1
                result.append((device, path))
        return result

    def __nt_places(self):
        result = []
        drives = windll.kernel32.GetLogicalDrives()
        for byte, letter in enumerate(ascii_uppercase):
            if drives & 1 << byte:
                result.append(("%s:" % letter, "%s:\\" % letter))
        return result
