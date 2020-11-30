"""
pyflowchart CLI

Copyright 2020 CDFMLR. All rights reserved.
Use of this source code is governed by a MIT
license that can be found in the LICENSE file.
"""

import sys
import argparse

from pyflowchart.flowchart import Flowchart


def main(code_file, field, inner):
    code = code_file.read()
    flowchart = Flowchart.from_code(code, field=field, inner=inner)
    print(flowchart.flowchart())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Python code to flowchart.')

    parser.add_argument('code_file',  type=argparse.FileType('r'))
    parser.add_argument('-f', '--field', default="", type=str, help="field to draw flowchart. (e.g. Class.method)")
    parser.add_argument('-i', '--inner', action="store_true", help="parse the body of field")

    args = parser.parse_args()

    if not args.field:  # field="", parse the whole file (ast Module), should use the body
        args.inner = True

    main(args.code_file, args.field, args.inner)
