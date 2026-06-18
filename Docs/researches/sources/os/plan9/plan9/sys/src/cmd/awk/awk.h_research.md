# File Research: sources/os/plan9/plan9/sys/src/cmd/awk/awk.h

Core Plan 9 awk interpreter header.

Key definitions:
- `Awkfloat` as `double`, `uschar`, `xfree`, and debug macro `dprintf`.
- Global interpreter state:
  - compile/run mode,
  - safe mode,
  - record and field state,
  - standard awk variables `FS`, `RS`, `ORS`, `OFS`, `OFMT`, `NR`, `FNR`, `NF`, `FILENAME`, `SUBSEP`, `RSTART`, `RLENGTH`,
  - regex match globals `patbeg` and `patlen`.
- `Cell`: variable/constant/function/field value with string, numeric value, type flags, and hash-chain link.
- `Array`: symbol table hash table.
- `Node`: parse-tree node with variable-length argument array.
- Type flags for numeric/string/array/function/field/record/constant storage.
- Builtin function IDs for length, sqrt, exp, log, int, system, rand/srand, sin/cos/atan, toupper/tolower, fflush, and utf.
- Cell subtypes, boolean subtypes, jump subtypes, node types, and helper macros for type tests.

Integration:
- Includes `proto.h` for interpreter function prototypes.
- Shared by parser, runtime, symbol table, regex, and execution modules.

Filesystem relevance:
- Indirect: awk can process files/streams, but this header is interpreter state, not filesystem code.
