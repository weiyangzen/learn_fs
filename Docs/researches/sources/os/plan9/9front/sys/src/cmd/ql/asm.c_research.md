# File Research: sources/os/plan9/9front/sys/src/cmd/ql/asm.c

This file emits final `ql` linker output. It writes text, data, symbols, line tables, dynamic relocation metadata, and executable headers for several PowerPC targets.

Key responsibilities:
- `entryvalue()` resolves the configured entry point, accepting numeric addresses or symbols.
- `asmb()` is the main output routine: emits text instructions via `asmout`, writes data blocks via `datblk`, optionally emits symbols and line tables, and then back-patches the file header.
- Header support includes boot format, Be PEF, Plan 9 format, raw output, AIX XCOFF, Blue Gene ELF, and Virtex 4 ELF boot images.
- `asmsym()` and `putsymb()` serialize Plan 9 symbol records for text, data, bss, files, autos, params, and frames.
- `asmlc()` emits compressed line-number deltas.
- `datblk()` materializes initialized data, performs endian conversion, handles float constants, string constants, symbol constants, duplicate initialization checks, and DLM relocations.

Important dependencies:
- Instruction encoding is delegated to `asmout.c`.
- Symbol/type state comes from `obj.c`, `pass.c`, and `span.c`.
- Dynamic relocation records are produced through `dynreloc()` in `span.c`.

Implementation notes:
- Output is buffered through `cput`, `wput`, `lput`, and `cflush`.
- All multi-byte output is big-endian, matching the PowerPC target.
- `datblk()` is sparse over linker data directives and writes zero-filled gaps.
