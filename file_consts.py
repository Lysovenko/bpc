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
"Some constants for file operations"

from os import X_OK, R_OK, W_OK

# file tuple positions
FT_NAME = 0
FT_TYPE = 1
FT_SIZE = 2
FT_TIME = 3
FT_MODE = 4

# mode flags
M_SYMLINK = 16
M_HIDDEN = 8
M_READABLE = R_OK
M_WRITEABLE = W_OK
M_EXECUTABLE = X_OK
