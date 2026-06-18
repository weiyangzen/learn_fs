# File Research: sources/os/plan9/9front/sys/src/cmd/hoc/hoc.y

Defines the yacc grammar, lexer, input handling, and top-level execution loop for `hoc`.

Key points:
- Grammar supports assignments, compound assignments, statements, returns, function/procedure calls, print lists, while/for/if/else, blocks, arithmetic, comparisons, logical operators, builtins, `read(var)`, pre/post increment/decrement, and function/procedure definitions.
- Grammar actions emit VM instructions using `code`, `code2`, and `code3`.
- Function/procedure definitions set symbol types, mark parser state as inside a definition, collect formals, emit a default `procret`, and call `define`.
- `yylex` tokenizes whitespace, backslash-newline continuations, `#` comments, numbers, identifiers, UTF-8-ish names, quoted strings with escapes, operators, and newlines.
- Unknown identifiers are installed as `UNDEF` and returned as `VAR`.
- `moreinput` supports stdin, file arguments, and `-e` inline expressions via temporary files.
- `run` uses `setjmp`/`longjmp` recovery and repeatedly initializes code, parses one top-level unit, and executes generated code.
- `execerror`, `yyerror`, `warning`, `fpecatch`, and `intcatch` provide error reporting and recovery.

Dependencies and interactions:
- Includes `hoc.h`, Plan 9 `Biobuf`, libc, and ctype.
- Calls VM functions from `code.c`, symbol functions from `symbol.c`, and initialization from `init.c`.

Research relevance:
- This file defines the language syntax and user-facing input/error behavior of `hoc`.
