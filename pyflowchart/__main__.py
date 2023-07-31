"""
pyflowchart CLI

Copyright 2020 CDFMLR. All rights reserved.
Use of this source code is governed by a MIT
license that can be found in the LICENSE file.
"""

import argparse

import chardet

from pyflowchart.flowchart import Flowchart

from pyflowchart.output_html import html_part_before_title,html_part_after_title_before_code_block,html_part_after_code_block_remaining_html
import os

def detect_decode(file_content: bytes) -> str:
    """detect_decode detect the encoding of file_content,
     then decode file_content on the detected encoding.

    If the confidence of detect result is less then 0.9,
    the UTF-8 will be used to decode. PyFlowchart is
    designed to convert Python 3 codes into flowcharts.
    And Python 3 is coding in UTF-8 in default. So only
    if we can make sure the file is not UTF-8 encoded (
    i.e. confidence > 0.9) than we will use that no
    default encoding to decoded it.

    Args:
        file_content: bytes: binary file content to decode

    Returns:
        str: decoded content
    """
    # detect encoding
    detect_result = chardet.detect(file_content)
    # print("DEBUG detect_result =", detect_result)

    encoding = detect_result.get("encoding")
    confidence = detect_result.get("confidence")

    if confidence < 0.9:
        encoding = "UTF-8"

    # decode file content by detected encoding
    try:
        content = file_content.decode(encoding=encoding)
    except TypeError:  # TypeError: decode() argument 1 must be str, not None
        content = file_content.decode()

    return content


def main(code_file, field, inner, output, simplify, conds_align):
    # read file content: binary
    file_content: bytes = code_file.read()
    # detect encoding and decode file content by detected encoding
    code = detect_decode(file_content)

    flowchart = Flowchart.from_code(code,
                                    field=field,
                                    inner=inner,
                                    simplify=simplify,
                                    conds_align=conds_align)
    print(flowchart.flowchart())
    #If output file was specified, 
    #Write output html format
    #html blocks stored as variables in output_html.py
    #html_part_before_title is header before <title>, 
    #If field specified use that as title. If not, use output filename as title.
    #Output remainder of header up to the code block (html_part_after_title_before_code_block)
    #Output the flowchart.flowchart() into the code block section of the html
    #Output the remainder of the html. (html_part_after_code_block_remaining_html)
    #End code block. Add couple buttons. Add output canvas.
    if bool(output):
        with open(output, 'w') as f:
            f.write(html_part_before_title)
            if bool(field):
                f.write(field)
            else:
                f.write(os.path.basename(f.name))
            f.write(html_part_after_title_before_code_block)
            f.write(flowchart.flowchart())
            f.write(html_part_after_code_block_remaining_html)
            print(f"Saved HTML togit co{output}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Python code to flowchart.')

    # code_file: open as binary, detect encoding and decode in main later
    parser.add_argument('code_file', type=argparse.FileType('rb'))

    parser.add_argument('-f', '--field', default="", type=str, help="field to draw flowchart. (e.g. Class.method)")
    parser.add_argument('-i', '--inner', action="store_true", help="parse the body of field")
    parser.add_argument('-o', '--output', default="", type=str, help="Output HTML file with flowchart")
    parser.add_argument('--no-simplify', action="store_false", help="do not simplify the one-line-body If/Loop")
    parser.add_argument('--conds-align', action="store_true", help="align consecutive If statements")

    args = parser.parse_args()

    if not args.field:  # field="", parse the whole file (ast Module), should use the body
        args.inner = True

    main(args.code_file, args.field, args.inner, args.output, args.no_simplify, args.conds_align)
