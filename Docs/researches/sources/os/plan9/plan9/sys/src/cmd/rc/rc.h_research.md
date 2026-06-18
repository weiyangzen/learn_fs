# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/rc.h

Primary shared header for rc.

Defines:
- Plan 9 vs Unix include boundary.
- parser depth and generated parser include.
- core typedefs for trees, words, I/O, code vectors, variables, lists, redirs, threads, and builtins.
- `tree` AST node with type, redirection/pipe details, string, quote/keyword flags, children, and allocation list.
- `union code` instruction word with function pointer/int/string variants and reference-count convention.
- token buffer `tok`, prompt state, redirection token constants, variable table, heredoc records, glob marker semantics, fd conventions, rcmain/fd prefix globals, and parser state globals.

Risk/notes:
- Many globals are definitions, not just declarations, reflecting old Plan 9 C style.
- `GLOB` escape representation is shared by lexer, globber, and printers.
