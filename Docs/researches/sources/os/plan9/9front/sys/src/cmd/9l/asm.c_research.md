# File Research: sources/os/plan9/9front/sys/src/cmd/9l/asm.c

This file writes the final linked output image. It emits text, data, symbol tables, line tables, optional dynamic relocation data, and binary headers for several Power64 output formats.

Key routines:
- `entryvalue` resolves the entry point from `INITENTRY`, accepting either numeric addresses or symbols.
- `asmb` is the top-level assembler writer. It writes text instructions through `asmout`, data blocks through `datblk`, symbols through `asmsym`, line tables through `asmlc`, optional dynamic data through `asmdyn`, and finally the output header.
- Header output supports boot/q.out/Plan 9/raw/ELF variants selected by `HEADTYPE`.
- `strnput`, `cput`, `wput`, `lput`, `llput`, and `cflush` implement buffered big-endian output.
- `asmsym` and `putsymb` emit Plan 9 symbol table entries for text, data, bss, file history, frames, autos, and parameters.
- `asmlc` encodes line-number deltas compactly.
- `datblk` materializes initialized data blocks from `ADATA`, `AINIT`, and `ADYNT` records, handling constants, strings, floats, endian maps, symbol-relative values, and dynamic relocations.

Important interactions:
- Calls `oplook` and `asmout` for instruction encoding.
- Consumes layout decisions made by `span` and `dodata`.
- Uses endian index arrays initialized by `nuxiinit` in `obj.c`.
- Calls `dynreloc` when data initializers reference symbols in dynamically loadable module mode.

Research notes:
- ELF output is 64-bit, big-endian PowerPC64.
- In DLM mode, data placement and relocation output are adjusted, and `HEADTYPE` is forced elsewhere to Plan 9 format.
- `datblk` detects overlapping initializers except for `AINIT`/`ADYNT`.
