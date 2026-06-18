# File Research: sources/os/plan9/9front/sys/src/cmd/1c/swt.c

Switch lowering, bitfield code, string/data object output, constant multiplication expansion, and ABI alignment for `1c`.

Key responsibilities:
- `doswit` collects, sorts, validates, and emits switch case dispatch.
- `swit1` emits linear dispatch for small switches and binary-search dispatch for larger switches.
- `bitload` and `bitstore` extract/update bitfields through shifts, masks, and memory writes.
- `outstring` and `outlstring` emit byte and Rune string data into `ADATA` records.
- `doinc` schedules pre/post increments around expression evaluation.
- `setsp` and `adjsp` emit stack-adjust pseudo-instructions.
- `outcode`, `zwrite`, `zname`, `zaddr`, and `outhist` serialize generated programs and histories into Plan 9 object format.
- `ieeedtod` serializes native doubles to target IEEE representation.
- `mulcon`, `shlcon`, and `mulcon1` expand constant multiplication using `multab`.
- `sextern`, `gextern`, `align`, and `maxround` handle external data emission and target ABI layout.

Notable details:
- `align` implements big-endian argument adjustment for sub-word parameters.
- Object writing mirrors the assembler’s compact address encoding so compiler output feeds the same linker.
