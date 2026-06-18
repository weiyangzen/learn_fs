# File Research: sources/os/plan9/9front/sys/src/cmd/2c/swt.c

Purpose: switch lowering, bit-field access, string/data/object output helpers, constant multiply expansion, and target layout rules.

Key behavior:
- `doswit()` collects, sorts, validates, and lowers switch cases through `swit1()`.
- `swit1()` chooses linear compare chains for small case counts, direct jump-table ranges for dense regions, and binary divide-and-conquer comparisons otherwise.
- `bitload()` and `bitstore()` implement signed/unsigned bit-field extraction and insertion with shifts/masks.
- `outstring()` and `outlstring()` emit byte and Rune string data into `ADATA` records under `symstring`.
- `doinc()` schedules pre/post increment and assignment side effects around expression generation.
- `setsp()`/`adjsp()` create stack-adjust pseudo-instructions; `eval()` forces non-addable expressions into registers.
- `outcode()`, `zwrite()`, `zname()`, `zaddr()`, and `outhist()` serialize compiler-emitted `Prog` lists into `.2` object files.
- `ieeedtod()` converts native doubles into simulated IEEE object format.
- `mulcon()`, `shlcon()`, and `mulcon1()` consume `multab[]` to generate shift/add/sub multiply sequences.
- `sextern()`/`gextern()` emit initialized global/static data.
- `align()` and `maxround()` define 68020 ABI layout/alignment, including big-endian argument adjustment.

Research notes:
- Direct switch tables are emitted as `ACASEW` plus static table entries materialized through `OCASE`/`ABCASE`.
- Object serialization here mirrors `2a/lex.c`; linker decoding is in `2l/obj.c`.
