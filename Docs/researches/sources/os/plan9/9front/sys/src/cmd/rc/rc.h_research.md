# File Research: sources/os/plan9/9front/sys/src/cmd/rc/rc.h

Primary shared header for `rc`. Selects Plan 9 vs Unix includes, defines parser depth, core typedefs, parse tree layout, code-vector convention, lexer state, variable structure, glob/UTF helpers, and global state declarations.

Important code-vector convention: `code[0]` is a reference count, `code[1]` is a source-file string, executable bytecode starts at pc 2, and vectors must be copied/freed through `codecopy()`/`codefree()`.

Defines redirection rtypes, variable hash size, token buffer size, pipe end constants, and global UI/runtime variables.
