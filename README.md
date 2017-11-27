# PyOne

This is a helper script for a quick and dirty one-liner in Python.
It converts a given script to properly indented Python code
and executes it. If a single expression is given it simply
eval it and displays the the retuen value.

## Usage

    pyone [-d] [-i modules] [-f modules] script [args ...]

## Examples

    $ pyone '2+3.4*5'
    19.0
    $ pyone -f sqlite3 'db=connect("foo.db"); \
         for row in db.execute("SELECT * FROM FOO;"){print(row)}'
    (123, 'Alice')
    (456, 'Bob')
    $ pyone -f urllib.request -f html.parser 'class P(HTMLParser){ \
         z=0; def handle_starttag(self,t,_){ if(t=="tr"){self.r=[]} \
         elif(t=="td"){self.z=1}} def handle_endtag(self,t){ \
         if(t=="tr"){print(",".join(self.r))}elif(t=="td"){self.z=0}} \
         def handle_data(self,s){if(self.z){self.r.append(s)}}} \
         P().feed(urlopen(argv[1]).read().decode("utf-8"))' \
         https://news.ycombinator.com/

## Command Line Options

 * `-d`         : debug mode. (dump the expanded code and exit)
 * `-i modules` : add `import modules` at the beginning of the script.
 * `-f modules` : add `from modules import *` for each module.

## Script Syntax

 * `;`          : inserts a newline and make proper indentation.

    A; B; C
   
    A
    B
    C

 * `{ ... }`    : makes the inner part indented.
 
    A { B; C }

    A:
        B
        C

 * `EL{ ... }`  : wraps the inner part as a loop executed for each line
                 of files specified by the command line (or stdin).
                 The following variables are available inside.

 ** `L`:   current line number (0-based).
 ** `S`:   current raw text, including `"\n"`.
 ** `s`:   stripped text line.
 ** `F[]`: splited fields with `DELIM`.
 ** `I[]`: integer value obtained from each field if any.

  More precisely, it inserts the folloing code:

    for (L,S) in enumerate(fileinput.input()):
        s = S.strip()
        F = s.split(DELIM)
        I = [ toint(v) for v in F ]
        (... your code here ...)

## Special variables

 * `DELIM` : field separator used in `EL { ... }` loop.
 * `argv`  : command line arguments.
