# File Research: sources/os/plan9/plan9/sys/src/cmd/lex/parser.y

Read fully: 653 lines, 14273 bytes. SHA-256 prefix: `dd3ce82327374264`.

This is the yacc grammar and lexical front-end for the `lex` specification language. The grammar parses definitions, delimiters, rules, actions, regular expressions, start conditions, right context, anchors, character classes, strings, alternation, concatenation, repetition, and counted iteration. Semantic actions build regex parse trees with `mn0()`, `mn1()`, `mn2()`, `mnp()`, and `dupl()`.

`yylex()` is a hand lexer for the lex input file. It handles:
- definition section directives like `%p`, `%n`, `%e`, `%o`, `%a`, `%k`, `%{...%}`, and `%s`,
- transition to rules at `%%`,
- action copying and generated case labels,
- quoted strings, character classes, escaped characters, definitions `{name}`, counted iterations, and start-condition lists `<...>`,
- section-three passthrough after the second delimiter.

`freturn()` exists under debug builds to report tokens.

Integration: produces parse-tree arrays consumed by `sub1.c` and `sub2.c`, and emits generated scanner action code through `fout`.

Risk notes: token buffers and generator tables have fixed limits with explicit errors. Action copying and section handling are sensitive to newline/indentation conventions.
