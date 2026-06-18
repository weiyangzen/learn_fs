# File Research: sources/os/plan9/9front/sys/src/cmd/tl/asm.c

`asm.c` is the ARM code and object-image emitter for `tl`, the Plan 9 ARM linker.

Major responsibilities:
- `entryvalue()` resolves numeric or symbolic entry point addresses.
- `asmb()` emits text, string literals, data, symbols, line tables, Thumb maps, dynamic metadata, and final executable headers.
- Output helpers `cput`, `wput`, `hput`, `lput`, `lputl`, and `cflush` manage buffered endian-specific writes.
- `asmsym()` and `putsymb()` emit Plan 9 symbol records.
- `asmlc()` emits compressed line-number tables.
- `asmthumbmap()` records Thumb code ranges.
- `datblk()` materializes initialized data and string blocks.

Instruction emission:
- `asmout()` maps `Optab.type` cases to ARM machine words.
- Handles arithmetic, moves, branches, loads/stores, halfword ops, floating point ops, switch/case ops, relocatable address loads, and ARM/Thumb interworking branch forms.
- Emits one to six 32-bit words depending on selected expansion size.
- `oprrr()`, `opbra()`, `olr()`, `olhr()`, `osr()`, `oshr()`, `olrr()`, `olhrr()`, `ofsr()`, and `omvl()` build instruction encodings.

File format support:
- Header type `0`: raw/no header.
- `1`: AIF/RISC OS.
- `2`: Plan 9.
- `3`: NetBSD boot.
- `4`: IXP1200 raw.
- `5`: iPAQ boot.

Risk notes:
- Many cases assume `span()` and `oplook()` have already selected valid expansions; errors here are often reported as diagnostics but output may continue until `errorexit`.
- `datblk()` detects multiple initialization except for `AINIT`/`ADYNT`, and does relocation handling for DLM mode.
- Thumb interworking behavior is controlled by `CALLEEBX` and symbol flags `thumb`, `foreign`, and `fnptr`.
