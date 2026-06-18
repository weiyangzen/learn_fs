# File Research: sources/os/plan9/9front/sys/src/cmd/awk/proto.h

Declares cross-file function prototypes for the awk implementation.

Key responsibilities:
- Declares parser, lexer, regex, main, parse-tree, symbol table, record/field, runtime execution, I/O redirection, substitution, and pipe functions.
- Provides the central compile-time interface between separately compiled awk modules.
- Declares generated dispatch table `proctab[]` and `tokname`.

Important interfaces:
- Included by `awk.h`, therefore shared across the awk source set.
- Covers modules not all present in this group, including `run.c` and `tran.c`.

Notes:
- The header carries the Lucent license block and uses Plan 9 C style declarations.
