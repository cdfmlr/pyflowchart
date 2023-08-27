import os


def output_html(output_name: str, field_name: str, flowchart: str) -> None:
    """
    This function outputting flowchart as html.

    This is derived from https://github.com/adrai/flowchart.js/blob/master/example/index.html
    and https://stackoverflow.com/a/64800570 with minor color and size changes.

    Use of this source code is governed by a MIT
    license that can be found in https://github.com/adrai/flowchart.js/blob/master/license

    Args:
        output_name: str : path to the dest file.
        field_name : str : title of the flowchart html page.
        flowchart  : str : the generated flowchart dsl (`Flowchart.flowchart()`).
    """

    # Three raw html code sections encapsulated in triple quotes """
    html_part_before_title = """<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>"""
    html_part_after_title_before_code_block = """</title>
        <style type="text/css">
          .end-element { fill : #FFCCFF; }
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/raphael/2.3.0/raphael.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/flowchart/1.17.1/flowchart.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.1/js/bootstrap.bundle.min.js"></script>
        <!-- <script src="../release/flowchart.min.js"></script> -->
        <script>

            window.onload = function () {
                var btn = document.getElementById("run"),
                    cd = document.getElementById("code"),
                    chart;
                    
                (btn.onclick = function () {
                    var code = cd.value;

                    if (chart) {
                      chart.clean();
                    }

                    chart = flowchart.parse(code);
                    chart.drawSVG('canvas', {
                      'x': 0,
                      'y': 0,
                      'line-width': 3,
                      //'maxWidth': 15,//ensures the flowcharts fits within a certain width
                      'line-length': 50,
                      'text-margin': 10,
                      'font-size': 14,
                      'font': 'normal',
                      'font-family': 'Helvetica',
                      'font-weight': 'normal',
                      'font-color': 'black',
                      'line-color': 'black',
                      'element-color': 'black',
                      'fill': 'white',
                      'yes-text': 'yes',
                      'no-text': 'no',
                      'arrow-end': 'block',
                      'scale': 1,
                      'symbols': {
                        'start': {
                          'font-size': 14,
                          'font-color': 'yellow',
                          'element-color': 'blue',
                          'fill': 'green',
                          'class': 'start-element'
                        },
                        'inputoutput': {
                          'font-color': 'black',
                          'element-color': 'black',
                          'fill': 'bisque'
                        },
                        'operation': {
                          'font-color': 'black',
                          'element-color': 'black',
                          'fill': 'linen'
                        },
                        'subroutine': {
                          'font-color': 'black',
                          'element-color': 'blue',
                          'fill': 'lightgreen'
                        },
                        'condition': {
                          'font-color': 'red',
                          'element-color': 'black',
                          'fill': 'yellow'
                        },
                        'end':{
                          'font-size': 20,
                          'class': 'end-element'
                        }
                      },
                      'flowstate' : {
                        //'past' : { 'fill' : '#CCCCCC', 'font-size' : 12},
                        //'current' : {'fill' : 'yellow', 'font-color' : 'red', 'font-weight' : 'bold'},
                        //'future' : { 'fill' : '#FFFF99'},
                        'request' : { 'fill' : 'blue'},
                        'invalid': {'fill' : '#444444'},
                        'approved' : { 'fill' : '#58C4A3', 'font-size' : 12, 'yes-text' : 'APPROVED', 'no-text' : 'n/a' },
                        'rejected' : { 'fill' : '#C45879', 'font-size' : 12, 'yes-text' : 'n/a', 'no-text' : 'REJECTED' }
                      }
                    });
                    //create base64 encoding of SVG to generate download link for title(without html or htm).SVG
                    var currentCanvasDIV = document.getElementById('canvas')
                    var currentDrawSVG = currentCanvasDIV.innerHTML.replaceAll('ë','e');

                    const OUTsvgBASE64 = btoa(currentDrawSVG)
                    doctitle = document.title.replace('.html','');
                    doctitle = doctitle.replace('.htm','');


                    var currentCanvasDIV = document.getElementById('canvas')
                    var currentDrawSVG = currentCanvasDIV.innerHTML.replaceAll('ë','e');
                    svgSource = currentDrawSVG
                    svgXML = currentDrawSVG;
                    // Use SVG Height and Width from the SVG XML to set canvas size
                    svgXMLsubstringHeight = svgXML.substring(svgXML.indexOf('height='), svgXML.indexOf('version='));
                    svgXMLsubstringWidth = svgXML.substring(svgXML.indexOf('width='), svgXML.indexOf('xmlns='));
                    HeightValue = svgXMLsubstringHeight.substring(svgXMLsubstringHeight.indexOf('"')+1,svgXMLsubstringHeight.lastIndexOf('"'));
                    WidthValue = svgXMLsubstringWidth.substring(svgXMLsubstringWidth.indexOf('"')+1,svgXMLsubstringWidth.lastIndexOf('"'));
                    HeightValueInt = Math.round(HeightValue)
                    WidthValueInt = Math.round(WidthValue)
                    // setup input for base64SvgToBase64Png
                    let svgSrc = "data:image/svg+xml;base64,"+OUTsvgBASE64;
                    var pngBase
                    imageUtil.base64SvgToBase64Png(svgSrc, WidthValueInt, HeightValueInt).then(pngSrc => {
                    pngBase = pngSrc
                    // output download link for base64 PNG converted on download from base64
                    var pngOutHtml = `<a href="${pngBase}" download="${doctitle}.png">PNG - Click here to download current rendered flowchart as ${doctitle}.png</a>`
                    document.getElementById("pngbase64").innerHTML=pngOutHtml;
                    });    
                    // output download link for base64 SVG converted on download from base64
                    var svgOutHtml = `<a href="data:image/svg+xml;base64,${OUTsvgBASE64}" download=${doctitle}.svg>SVG - Click here to download current rendered flowchart as ${doctitle}.svg</a> `
                        document.getElementById("svgbase64").innerHTML=svgOutHtml;
                    })();

                            };
                 

// derived from https://stackoverflow.com/a/64800570
// we need to use web browser canvas to generate a image. In this case png
let imageUtil = {};
/**
 * converts a base64 encoded data url SVG image to a PNG image
 * @param originalBase64 data url of svg image
 * @param width target width in pixel of PNG image
 * @param secondTry used internally to prevent endless recursion
 * @return {Promise<unknown>} resolves to png data url of the image
 */
imageUtil.base64SvgToBase64Png = function (originalBase64, width, height, secondTry) {
    return new Promise(resolve => {
        let img = document.createElement('img');
        img.onload = function () {
            if (!secondTry && (img.naturalWidth === 0 || img.naturalHeight === 0)) {
                let svgDoc = base64ToSvgDocument(originalBase64);
                let fixedDoc = fixSvgDocumentFF(svgDoc);
                return imageUtil.base64SvgToBase64Png(svgDocumentToBase64(fixedDoc), width, height, true).then(result => {
                    resolve(result);
                });
            }
            //document.body.appendChild(img);
            let canvas2 = document.createElement("canvas");
            //document.body.removeChild(img);
            canvas2.width = width;
            canvas2.height = height;
            let ctx = canvas2.getContext("2d");
            ctx.drawImage(img, 0, 0, canvas2.width, canvas2.height);
            try {
                let data = canvas2.toDataURL('image/png');
                resolve(data);
            } catch (e) {
                resolve(null);
            }
        };
        img.src = originalBase64;
    });
}

//needed because Firefox doesn't correctly handle SVG with size = 0, see https://bugzilla.mozilla.org/show_bug.cgi?id=700533
function fixSvgDocumentFF(svgDocument) {
    try {
        let widthInt = parseInt(svgDocument.documentElement.width.baseVal.value) || 500;
        let heightInt = parseInt(svgDocument.documentElement.height.baseVal.value) || 500;
        svgDocument.documentElement.width.baseVal.newValueSpecifiedUnits(SVGLength.SVG_LENGTHTYPE_PX, widthInt);
        svgDocument.documentElement.height.baseVal.newValueSpecifiedUnits(SVGLength.SVG_LENGTHTYPE_PX, heightInt);
        return svgDocument;
    } catch (e) {
        return svgDocument;
    }
}

function svgDocumentToBase64(svgDocument) {
    try {
        let base64EncodedSVG = btoa(new XMLSerializer().serializeToString(svgDocument));
        return 'data:image/svg+xml;base64,' + base64EncodedSVG;
    } catch (e) {
        return null;
    }
}

function base64ToSvgDocument(base64) {
    let svg = atob(base64.substring(base64.indexOf('base64,') + 7));
    svg = svg.substring(svg.indexOf('<svg'));
    let parser = new DOMParser();
    return parser.parseFromString(svg, "image/svg+xml");
} 
        </script>

        <script>
            function HelpText() {
              var x = document.getElementById("HelpTextBlock");
              if (x.style.display === "none") {
                x.style.display = "block";
              } else {
                x.style.display = "none";
              }
            }
        </script>
    </head>
    <body>
        <div><textarea id="code" style="width: 100%;" rows="11">"""

    html_part_after_code_block_remaining_html = """</textarea></div>
        <div><button id="run" type="button">Run</button> <button onclick="HelpText()">Format Help</button></div>
        <div id="HelpTextBlock" style="display:none"><br/>Conditions can also be redirected like cond(yes, bottom) or cond(yes, right)
... and the other symbols too... like sub1(right)<br/>
You can also tweak the <b>diagram.drawSVG('diagram', {});</b> script in this file for more changes<br/>
This is based on <a href="https://github.com/adrai/flowchart.js">flowchart.js on github</a> and <a href="http://flowchart.js.org">http://flowchart.js.org</a> more documentation can be found over there.
</div><br/><div id="svgbase64"></div>
        <div id="pngbase64"></div>

        <div id="canvas"></div>
    </body>
</html>"""
    # No checking or prompting if output file already exists.
    # This will overwrite if given an existing output file
    with open(output_name, 'w', encoding="utf-8") as f:
        # html_part_before_title is header before <title>, 
        f.write(html_part_before_title)
        # If field specified use that as title. If not, use output filename as title.
        if bool(field_name):
            f.write(field_name)
        else:
            f.write(os.path.basename(f.name))
        # Output remainder of header up to the flowchart code block (html_part_after_title_before_code_block)
        f.write(html_part_after_title_before_code_block)
        # Output the flowchart into the code block section of the html
        f.write(flowchart)
        # Output the remainder of the html. (html_part_after_code_block_remaining_html)
        # End code block. Add couple buttons. Add output canvas.
        f.write(html_part_after_code_block_remaining_html)
        # Print to console confirming to end user it was saved.
        print(f"Saved HTML to {output_name}")
