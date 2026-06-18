# File Research: sources/os/plan9/9front/sys/src/cmd/lex/parser.y

This yacc grammar parses lex input and builds the regular-expression parse tree used to generate the scanner.

Grammar coverage:
- Definitions section: macro definitions, `%` directives, `%{...%}` copied code, `%s` start conditions, and size overrides (`%p`, `%n`, `%e`, `%o`, `%a`, `%k`).
- Rules section: regex/action pairs, blank-leading action continuations, `|` action reuse, included code, and section delimiter.
- Regex operators: literals, strings, `.`, character classes, negated classes, `*`, `+`, `?`, alternation, concatenation, trailing context `/`, end anchor `$`, start anchor `^`, start conditions, null strings, and bounded repetitions `{n}`, `{n,m}`, `{n,}`.

The embedded `yylex()` is a hand-coded scanner for lex source syntax. It expands definitions, parses character classes/ranges, handles escapes, copies user action code with `cpyact()`, and emits generated scanner action cases.

This file ties syntax recognition directly to parse-tree constructors (`mn0`, `mn1`, `mn2`, `mnp`, `dupl`) and code emission (`phead2`, `ptail`).
