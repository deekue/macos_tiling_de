#!/usr/bin/env python3
#
# parse a marked up config file (ala Remontoire) and output JSON
#
# config ->
#   [ {'category': str, 'actions': [ { 'action': str, 'keys': str }, ], ]
#
# inspired by
# https://github.com/regolith-linux/remontoire/blob/master/src/config_parser.vala
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
<html>
<head>
 <title>Key Bindings</title>
 <link href="https://unpkg.com/@primer/css/dist/primer.css" rel="stylesheet" />
</head>
<body>
 <table>
  <thead>
   <tr><th>Action</th><th>Keybinding</th></tr>
  </thead>
  <tbody>
"""

HTML_FOOTER = """
  </tbody>
 </table>
</body>
</html>
"""

HTML_CATEGORY_START = '<tbody id="{category}"><tr><th>{category}</th><th>&nbsp;</th></tr>'
HTML_CATEGORY_END = '</tbody>'
HTML_KEYSPEC = '<tr><td>{label}</td><td>{keys}</td></tr>'


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
    parser = argparse.ArgumentParser()
    parser.add_argument('-f',
                        '--format',
                        help='output format',
                        choices=['html', 'json', 'data'],
                        default='html')
    parser.add_argument('-o', '--output', help='output to')
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
        outputFile = open(args.output, 'w')
    else:
        outputFile = sys.stdout
    if outputFormat == 'html':
        outputHTML(tree, file=outputFile)
    elif outputFormat == 'json':
        outputJSON(tree, file=outputFile)
    elif outputFormat == 'data':
        outputData(tree, file=outputFile)
    else:
        parser.print_help()
