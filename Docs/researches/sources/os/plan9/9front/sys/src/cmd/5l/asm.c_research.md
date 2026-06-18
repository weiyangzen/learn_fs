# File Research: sources/os/plan9/9front/sys/src/cmd/5l/asm.c

This file is the final output and machine-code emission stage for the ARM linker `5l`. It writes executable headers, text, data, symbols, line tables, dynamic relocation data, and ARM instruction encodings.

Key elements:
- `entryvalue()` resolves `INITENTRY` to either a numeric address, text symbol, or DLM data symbol.
- `asmb()` emits text instructions, string constants in text, initialized data blocks, symbol/line/dynamic tables, and the selected executable header.
- Header formats include raw/no-header, AIF, Plan 9, NetBSD boot, IXP1200 raw, iPAQ, and ELF.
- `cput()`, `wput()`, `lput()`, `lputl()`, and `cflush()` implement buffered byte/word/long output with endian choices.
- `asmsym()` writes Plan 9 symbol records for text, data, BSS, string, file, frame, auto, and parameter symbols.
- `asmlc()` emits compressed line-number deltas.
- `datblk()` materializes initialized data and text-string blocks from `ADATA`, `AINIT`, and `ADYNT`.
- `asmout()` maps `Optab` cases to one to six ARM words.
- Helpers such as `oprrr()`, `opbra()`, `olr()`, `olhr()`, `osr()`, `ofsr()`, `omvl()`, and `chipfloat()` build specific ARM, old ARM FPA, and VFP encodings.

Dependencies and integration:
- Consumes `Prog` lists and `Optab` classifications from earlier linker passes.
- Uses data layout from `dodata()`, symbol types from `l.h`, and operand classes from `span.c`.
- Adds DLM relocation records through `dynreloc()` when required.

Notable behavior:
- `asmout()` is table-type driven: each `Optab.type` encodes a small code-generation recipe.
- Long constants and long addresses are loaded through literal pools via `omvl()` when `p->cond` points to a pool entry.
- VFP support is selected by global `vfp`; otherwise old ARM 7500-style coprocessor floating-point encodings are used.
- `datblk()` checks for multiple initialization except for DLM init/dynt and duplicate-ok symbols.
- Some emitted ELF comments still refer to PPC flags, but the machine field is ARM.

Research notes:
- This file is the most architecture-specific part of `5l`.
- It assumes earlier passes have resolved PC values, branches, literal pools, data placement, and operand classes correctly.
