#!/usr/bin/env python
# -*-python-*-

##  PyOne - Python One-liner helper
##  Author: Yusuke Shinyama
##
##  Usage:
##    $ pyone [-d] [-i modules] [-f modules] script [args ...]
##
##  Description:
##    This is a helper script for quick and dirty one-liner in Python.
##    It converts a given script to properly indented Python code
##    and executes it. If a single expression is given it simply
##    eval it and displays the the retuen value.
##
##  Options:
##    -d         : debug mode. (dump the expanded code and exit)
##    -i modules : add 'import modules' at the beginning of the script.
##    -f modules : add 'from modules import *' for each module.
##
##  Syntax:
##    ;          : inserts a newline and make proper indentation.
##                 ex. "A; B; C" is expanded as
##
##      A
##      B
##      C
##
##    { ... }    : makes the inner part indented.
##                 ex. "A { B; C }" is expanded as
##
##      A:
##          B
##          C
##
##    EL{ ... }  : wraps the inner part as a loop executed for each line
##                 of files specified by the command line (or stdin).
##                 The following variables are available inside.
##
##      L:   current line number (0-based).
##      S:   current raw text, including "\n".
##      s:   stripped text line.
##      F[]: splited fields with DELIM.
##      I[]: integer value obtained from each field if any.
##
##      Precisely, it inserts the folloing code:
##
##      for (L,S) in enumerate(fileinput.input()):
##          s = S.strip()
##          F = s.split(DELIM)
##          I = [ toint(v) for v in F ]
##          (... your code here ...)
##
##  Special variables:
##    DELIM : field separator used in EL { } loop.
##    argv  : command line arguments.
##
##  Examples:
##    $ pyone '2+3.4*5'
##    $ pyone -f sqlite3 'db=connect("foo.db"); \
##         for row in db.execute("SELECT * FROM FOO;"){print(row)}'
##    $ pyone -f urllib.request -f html.parser 'class P(HTMLParser){ \
##         z=0; def handle_starttag(self,t,_){ if(t=="tr"){self.r=[]} \
##         elif(t=="td"){self.z=1}} def handle_endtag(self,t){ \
##         if(t=="tr"){print(",".join(self.r))}elif(t=="td"){self.z=0}} \
##         def handle_data(self,s){if(self.z){self.r.append(s)}}} \
##         P().feed(urlopen(argv[1]).read().decode("utf-8"))' \
##         https://news.ycombinator.com/
##

import sys
import re
import fileinput


##  User objects (seen from the script)
##

# DELIM:
#   Field separator used in EL{ }.
global DELIM
DELIM = ' '

# toint(x):
#   Converts a string to an interger if possible,
#   otherwise returns 0.
def toint(x, v=0):
    try:
        return int(x)
    except ValueError:
        return v


##  Perform macro expansion
##
PAT = re.compile(
    '[^\042\047{};]*'
    '([{};]|'
    '\042(\\\\.|[^\042])*\042|'
    '\047(\\\\.|[^\047])*\047)')
def make_script(s):
    # Each time pat1 matches from the beginning of the string
    # to the first occurrence of ";", "{", or "}".
    # Occurrences in quotation are skipped.
    indent = 0  # current indentation.
    lines = []
    def add(line):
        line = line.strip()
        if line:
            lines.append('    '*indent + line)
        return
    b = i = 0
    while i < len(s):
        m = PAT.match(s, i)
        if not m:
            add(s[b:])
            break
        e = m.end(0)
        if s[e-3:e] == 'EL{':
            # EL{ ... } macro expansion.
            add(s[b:e-3])
            add('for (L,S) in enumerate(fileinput.input()):')
            indent = indent + 1
            add('s = S.strip()')
            add('F = s.split(DELIM)')
            add('I = [ toint(v) for v in F ]')
        elif s[e-1] == '{':
            add(s[b:e-1]+':')
            indent = indent + 1
        elif s[e-1] == '}':
            add(s[b:e-1])
            indent = indent - 1
            if indent < 0: raise SyntaxError('Invalid Syntax: '+s[b:])
        elif s[e-1] == ';':
            add(s[b:e-1])
        else:
            i = e
            continue
        b = i = e
    return lines

# main
def main(argv):
    # preserve the current environment.
    _globals = globals().copy()
    _locals = locals().copy()
    import getopt
    # get options.
    def usage():
        print('usage: %s [-d] [-i modules] [-f modules] [-F delim] script [args ...]' %
              argv[0])
        return 111
    try:
        opts, args = getopt.getopt(argv[1:], 'di:f:F:')
    except getopt.error:
        return usage()
    
    debug = 0
    lines = []
    for (k, v) in opts:
        if k== '-d':
            debug += 1
        elif k == '-i':
            lines.append('import %s' % v)
        elif k == '-f':
            lines.extend([ 'from %s import *' % m for m in v.split(',') ])
                         
    if not args: return usage()

    lines.extend(make_script(args[0]))
    script = '\n'.join(lines)
    
    # debug mode
    if debug:
        print(script)
        return 0
    
    # hand the remaining args to the runtime environment.
    _locals['argv'] = args
    sys.argv = args
    path = '<script>'
    if len(lines) == 1:
        # real one-liner
        r = eval(compile(script, path, 'single'))
        if r is not None:
            print(r)
    else:
        eval(compile(script, path, 'exec'), _globals, _locals)
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
