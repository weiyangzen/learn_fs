# File Research: sources/os/plan9/9front/sys/src/cmd/awk/awk.h

Defines core data structures, globals, constants, and macros for the Plan 9 awk implementation.

Key responsibilities:
- Defines `Awkfloat`, debug macros, record-size defaults, and standard `Biobuf` globals.
- Declares builtin variable pointers such as `FS`, `RS`, `ORS`, `OFS`, `NR`, `FNR`, `NF`, `FILENAME`, `SUBSEP`, `RSTART`, and `RLENGTH`.
- Defines `Cell`, the variable/value representation used for scalars, arrays, fields, constants, functions, and temporaries.
- Defines `Array`, the hash table representation for awk arrays and symbol tables.
- Defines `Node`, the parse-tree node representation.
- Defines cell flags, builtin function IDs, node types, ctype/csub values, and jump/bool classifications.
- Includes `proto.h`.

Important interfaces:
- Shared by lexer, parser, runtime, regex, I/O, and generated dispatch code.
- Provides macros like `isstr`, `isnum`, `isarr`, `isfcn`, `freeable`, and `notlegal`.

Notes:
- Carries Lucent copyright notice.
