# File Research: sources/os/plan9/plan9/sys/src/cmd/hoc/hoc.y

Yacc grammar, lexer, input driver, and error recovery for `hoc`.

- Grammar supports assignments, compound assignments, expressions, `print`, `read`, `if/else`, `while`, `for`, statement blocks, functions, procedures, returns, formal parameters, and argument lists.
- Expression grammar includes arithmetic, `%`, exponentiation, comparisons, logical operators, unary minus, logical not, and pre/post increment/decrement.
- Parser actions emit VM instructions into `prog[]` using `code`, `code2`, and `code3`.
- Lexer recognizes numbers via `Bgetd`, identifiers including high-bit bytes, quoted strings with simple escapes, comments beginning `#`, continuation backslash-newline, and multi-character operators.
- Main input loop supports stdin, file arguments, and `-e` expressions via temporary files.
- Runtime and parse errors call `execerror()`, flush remaining input, restore formal bindings, and longjmp to the top-level parse loop.

Dependencies are `hoc.h`, `bio`, `ctype`, libc, generated `y.tab.h`, and the VM in `code.c`.

Notable concerns: identifiers and strings are limited to 99 bytes. Error recovery seeks to end of the current input file, so one bad expression can skip the rest of that file.
