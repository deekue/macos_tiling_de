#!/usr/bin/env python3
#
# parse a marked up config file (ala Remontoire) and output JSON
#
# config ->
#   [ {'category': str, 'actions': [ { 'action': str, 'keys': str }, ], ]
#
# inspired by
# https://github.com/regolith-linux/remontoire/blob/master/src/config_parser.vala
# data URI: https://stackoverflow.com/questions/9045584/opening-standard-stream-in-google-chrome
#
# TODO
# - add heuristic to find common configs?

import argparse
import html
import json
import os
import re
import sys

LINE_RE = re.compile(
    r'^##(?P<category>.*?)//(?P<action>.*?)//(?P<keys>.*?)##.*$')
VERBOSE = False

HTML_HEADER = """
<!DOCTYPE html>
<!--
expando rows from https://codepen.io/aardrian/pen/VoQbLm
key shortcuts from https://www.webmound.com/create-keyboard-shortcuts-in-javascript/
  -->
<html>
  <head>
    <title>Key Bindings</title>
    <!-- styling for kbd tag -->
    <link href="https://unpkg.com/@primer/css/dist/primer.css" rel="stylesheet" />
    <style>
body {
  line-height: 1.4;
  background: #fefefe;
  color: #333;
  margin: 0 1em;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
footer {
  margin-top: auto;
}

.row table {
  margin: 1em 0;
  border-collapse: collapse;
  min-width: 100%;
}

.row th {
  padding: 0.25em 0.5em 0.25em 1em;
  text-indent: -0.5em;
  vertical-align: bottom;
  background-color: rgba(0, 0, 0, 0.75);
  color: #fff;
  font-weight: bold;
}

.row td:nth-of-type(2) {
  padding: 0.25em 0.5em 0.25em 1em;
  vertical-align: text-top;
  text-indent: -0.5em;
}

.row th:nth-of-type(3),
.row td:nth-of-type(3) {
  text-align: right;
}

.row td[colspan] {
  background-color: #fefefe;
  color: #000;
  font-weight: bold;
  padding: 0;
  text-indent: 0;
}

tr.shown, tr.hidden {
  display: table-row;
}

tr.hidden {
  display: none;
}

.row button {
  background-color: transparent;
  border: .1em solid transparent;
  font: inherit;
  padding: 0.25em 0.5em 0.25em .25em;
  width: 100%;
  text-align: left;
}

.row button svg {
  width: .8em;
  height: .8em;
  margin: 0 0 -.05em 0;
  fill: #66f;
  transition: transform 0.25s ease-in;
  transform-origin: center 45%;
  transform: rotate(-90deg);
}

.row button:hover svg,
.row button:focus svg {
  fill: #00c;
}

.row button:focus, .row button:hover {
  background-color: #ddd;
  outline: .2em solid #111;
}

/* Lean on programmatic state for styling */
.row button[aria-expanded="true"] svg {
  transform: rotate(0deg);
}

    </style>
    <script>
      function modulo(n, m) {
        return ((n % m) + m) % m;
      }
      document.addEventListener('keydown', (e) => {
        var buttons = Array.from(document.getElementsByTagName('button'));
        var current = document.activeElement;

        const curIndex = buttons.findIndex(({id}) => id === current.id);
        // h j k l - left up down right
        if (e.key.toLowerCase() === 'j' || e.key === 'ArrowDown') {
          var newIndex = modulo((curIndex + 1), buttons.length);
          buttons[newIndex].focus();
        } else if (e.key.toLowerCase() === 'k' || e.key === 'ArrowUp') {
          var newIndex = modulo((curIndex - 1), buttons.length);
          buttons[newIndex].focus();
        } else if (e.key.toLowerCase() === 'h' || e.key === 'ArrowLeft') {
          setRowVisibility(current.id, false);
        } else if (e.key.toLowerCase() === 'l' || e.key ==='ArrowRight') {
          setRowVisibility(current.id, true);
        } else if (e.key.toLowerCase() === 'a') {
          setAllRowVisibility(true);
        } else if (e.key.toLowerCase() === 'x') {
          setAllRowVisibility(false);
        } else if (e.key === 'Home') {
          buttons[0].focus();
        } else if (e.key === 'End') {
          buttons[buttons.length - 1].focus();
        }
      });

      function setAllRowVisibility(show) {
        var theTBodys = document.getElementsByTagName('tbody');
        for (var i = 0; i < theTBodys.length; i++) {
          var id = theTBodys[i].id;
          setRowVisibility('btn' + id, show);
        }
      }

      function setRowVisibility(btnID, show) {
        var theButton = document.getElementById(btnID);
        var tbodyID = btnID.substring(3);
        var theRows = document.getElementById(tbodyID).getElementsByTagName("tr");

        for (var i = 1; i < theRows.length; i++) {
          theRows[i].classList.add(show ? "shown" : "hidden");
          theRows[i].classList.remove(show ? "hidden" : "shown");
        }
        theButton.setAttribute("aria-expanded", show ? "true" : "false");
      }

      function toggleButton(btnID) {
        var theButton = document.getElementById(btnID);
        var toggleState = theButton.getAttribute("aria-expanded") == "true" ? false : true;

        setRowVisibility(btnID, toggleState);
      }
    </script>
  </head>
  <body>
    <table class="row">
      <thead>
        <tr>
          <th colspan="2">Action</th>
          <th>Keybinding</th>
        </tr>
      </thead>
"""

HTML_FOOTER = """
  </tbody>
 </table>
 <footer>
   <table>
   <tr><td><kbd>j</kbd>&nbsp;<kbd>k</kbd></td><td>move down/up</td></tr>
   <tr><td><kbd>h</kbd>&nbsp;<kbd>l</kbd></td><td>close/open</td></tr>
   <tr><td><kbd>a</kbd></td><td>open all</td></tr>
   <tr><td><kbd>x</kbd></td><td>close all</td></tr>
   </table>
 </footer>
</body>
</html>
"""

HTML_CATEGORY_START = '''<tbody id="{category}">
        <tr>
          <td colspan="3">
            <button type=button id="btn{category}" aria-expanded="false" onclick="toggleButton(this.id);" aria-label="{category}">
              <svg xmlns="\http://www.w3.org/2000/svg&quot;" viewBox="0 0 80 80" focusable="false">
                <path d="M70.3 13.8L40 66.3 9.7 13.8z"></path>
              </svg>
              {category}
            </button>
          </td>
        </tr>'''
HTML_CATEGORY_END = '</tbody>'
HTML_KEYSPEC = '<tr class="hidden"><td></td><td>{label}</td><td>{keys}</td></tr>'


def log(*args):
    if VERBOSE:
        print(file=sys.stderr, *args)


def readFromFile(filename):
    """Read config from file, return lines iterator."""
    return open(filename, 'r').readlines


def readFromIPC(socket):
    """Read config from IPC via socket, return lines."""
    pass


def parseKeys(line):
    tokens = []
    str_builder = []

    for c in line:
        if c == '<':
            if len(str_builder) > 0:
                tokens.append(''.join(str_builder))
                str_builder.clear()
            str_builder.append(c)
        elif c == '>':
            str_builder.append(c)
            tokens.append(''.join(str_builder))
            str_builder.clear()
        elif c == ' ':
            if len(str_builder) > 0:
                tokens.append(''.join(str_builder))
                str_builder.clear()
        else:
            str_builder.append(c)

    if len(str_builder) > 0:
        tokens.append(''.join(str_builder))

    return tokens


def parseLine(line):
    m = LINE_RE.match(line)
    if m is None:
        return None
    groups = m.groupdict()
    if any((i is None for i in groups.values())):
        return None
    category = groups['category'].strip()
    action = groups['action'].strip()
    keys = parseKeys(groups['keys'].strip())
    return (category, action, keys)


def parseConfig(config_iter):
    """Parse lines in config_iter, return tree."""
    log('parseConfig')
    catTree = {}
    for line in config_iter():
        parsedItems = parseLine(line)
        if parsedItems is None:
            continue
        (category, action, keys) = parsedItems
        catTree.setdefault(category, []).append({
            'action': action,
            'keys': keys
        })

    # flatten for easier rendering
    log('  flatten')
    catList = []
    for k, v in catTree.items():
        catList.append({'category': k, 'actions': v})
    return catList


def outputJSON(tree, pretty=False, file=sys.stdout):
    log('outputJSON')
    if pretty:
        print(json.dumps(tree, indent=4, separators=(',', ': ')), file=file)
    else:
        print(json.dumps(tree), file=file)


def escapeKey(key):
    return html.escape(key).encode('ascii', 'xmlcharrefreplace').decode()

def formatKeys(keys):
    formattedKeys = []
    keys.reverse()

    for key in keys:
        if key.startswith('<') and key.endswith('>'):
            css_class = 'metakey'
            key = key[1:-1] # strip <>
            key = f'<kbd class="{css_class}">{escapeKey(key)}</kbd>'
        elif '..' in key:
            css_class = 'rangekey'
            (range_start, range_end) = key.split('..')
            key = f'<span class="{css_class}"> <kbd>{escapeKey(range_start)}</kbd>..<kbd>{escapeKey(range_end)}</kbd></span>'
        elif key == "or":
            key = f' or '
        else:
            key = f' <kbd>{escapeKey(key)}</kbd>'

        formattedKeys.insert(0, key)
    return ''.join(formattedKeys)


def outputHTML(tree, file=sys.stdout):
    log('outputHTML')
    print(HTML_HEADER, file=file, end='')
    # walk tree, convert to HTML UL
    for item in tree:
        (category, actions) = item.values()
        print(HTML_CATEGORY_START.format(category=html.escape(category)),
              file=file,
              end='')
        for action in actions:
            (label, keys) = action.values()
            print(HTML_KEYSPEC.format(label=html.escape(label),
                                      keys=formatKeys(keys)),
                  file=file,
                  end='')
        print(HTML_CATEGORY_END, file=file, end='')
    print(HTML_FOOTER, file=file, end='')


def outputData(tree, file=sys.stdout):
    import base64
    from io import StringIO

    output = StringIO()
    outputHTML(tree, file=output)
    encodedHTML = base64.b64encode(output.getvalue().encode()).decode()
    print(f'data:text/html;base64,{encodedHTML}', file=file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-f',
                        '--format',
                        help='output format',
                        choices=['html', 'json', 'data'],
                        default='html')
    parser.add_argument('-o', '--output',
                        help='output to',
                        default='~/.cache/skhd/skhd.html')
    parser.add_argument('-c',
                        '--config',
                        help='SKHD config to parse',
                        default='~/.config/skhd/skhdrc')
    parser.add_argument('-v',
                        '--verbose',
                        help='verbose output to stderr',
                        action='store_true',
                        default=False)
    args = parser.parse_args()

    outputFormat = args.format.lower()
    VERBOSE = args.verbose
    tree = parseConfig(readFromFile(os.path.expanduser(args.config)))
    if args.output:
        if args.output == "-":
            outputFile = sys.stdout
        else:
            outputFile = open(os.path.expanduser(args.output), 'w')
    if outputFormat == 'html':
        outputHTML(tree, file=outputFile)
    elif outputFormat == 'json':
        outputJSON(tree, file=outputFile)
    elif outputFormat == 'data':
        outputData(tree, file=outputFile)
    else:
        parser.print_help()
