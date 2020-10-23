"""
pyflowchart CLI

Copyright 2020 CDFMLR. All rights reserved.
Use of this source code is governed by a MIT
license that can be found in the LICENSE file.
"""

import sys

from pyflowchart.flowchart import Flowchart

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("pyflowchart: Python code to flowchart\nUsage: pyflow py_file")

    file_name = sys.argv[1]
    with open(file_name) as f:
        code = f.read()

    flowchart = Flowchart.from_code(code)
    print(flowchart.flowchart())
