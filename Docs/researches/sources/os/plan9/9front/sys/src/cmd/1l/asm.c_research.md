# File Research: sources/os/plan9/9front/sys/src/cmd/1l/asm.c

Final assembler/emitter for the Plan 9 `1l` 68000 linker.

Key responsibilities:
- `entryvalue` resolves numeric or symbolic entry points.
- `asmb` writes text, data, symbols, stack/line tables, relocations, and output headers for supported `HEADTYPE`s.
- Supports Plan 9 a.out variants, boot formats, NeXT boot/Mach-style headers, and Pilot relocatable output.
- `asmins` encodes each `Prog` into 68000/68881 instruction words using `optab`.
- Handles special control registers, CCR/SR/USP/move-control, FP control registers, branches, moves, arithmetic, shifts, FP ops, bitfields, movem/fmovem, traps, and pseudo-ops.
- `asmea` converts `Adr` operands into effective-address encodings and emits extension words.
- `datblk` materializes initialized data blocks, catches overlapping initialization, and writes constants, strings, floats, and symbol-relative values.
- `asmreloc` writes Pilot relocation records.
- Provides endian/output helpers `lput`, `s16put`, `cflush`, `gnuxi`, and `rnd`.

Notable details:
- Branch sizing supports short/word encodings and absolute long branch fallback for `BRA/BSR`.
- Data symbol addressing prefers A6-relative small-data form when possible.
