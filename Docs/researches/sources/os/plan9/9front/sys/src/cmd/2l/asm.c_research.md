# File Research: sources/os/plan9/9front/sys/src/cmd/2l/asm.c

Purpose: final binary emitter and 68020 instruction encoder for linker `2l`.

Key behavior:
- `entryvalue()` resolves numeric or symbolic entry point.
- `asmb()` writes text instructions, data blocks, symbol table, stack maps, line maps, and executable headers for supported `HEADTYPE`s: legacy, Plan 9 boot, Plan 9, NeXT boot, and preprocess pilot.
- During text emission it checks span phase consistency, calls `asmins()` for each instruction, writes big-endian words to output buffer, and supports debug assembly listings.
- `asmins()` encodes each instruction using `optab[p->as].optype`, with special handling for CCR/SR/USP/control registers, FPU control registers, branches, moves, arithmetic, compare, shifts, FPU ops, bit-fields, MOVEM/FMOVEM, trap, CASEW/BCASE, MOVES, and SWAP.
- `asmea()` converts `Adr` operands into 68020 effective-address mode bits and extension words, handling direct registers, stack/TOS, branches, constants, FPU constants, quick immediates, auto/param/static/extern references, absolute addresses, A6-relative data, text references, and 68020 full indexed addressing.
- `datblk()` materializes initialized data chunks from `ADATA` records, detects overlapping initialization, resolves symbol addresses, and writes target byte order.
- `gnuxi()` and `nuxi` tables control float/integer byte ordering; `lput()`, `s16put()`, `cflush()`, and `rnd()` support file output.

Research notes:
- `ABCASE` is converted into data-table entries relative to `casepc`.
- Some branch/call encodings are selected based on final PC range, e.g. a far branch may use long extension words.
- Undefined externals are diagnosed in `asmea()` and forced to data type to continue error collection.
