# File Research: sources/os/plan9/plan9/sys/src/cmd/awk/proto.h

Cross-module prototypes for the awk implementation.

Covers parser, lexer, regex interface, AST construction, symbol table management, record/field handling, diagnostics, runtime execution, built-ins, I/O redirection, substitution, and Plan 9/ANSI C library hooks such as `popen`/`pclose`.

This header documents the major internal subsystem boundaries: scanner/parser, regex adapter, parse tree builder, symbol table/type conversion, record library, and interpreter runtime.
