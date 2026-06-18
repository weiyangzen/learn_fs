# File Research: sources/os/plan9/9front/sys/src/cmd/vl/asm.c

This is the MIPS linker backend emitter for `vl`. It writes executable text/data, Plan 9 symbol and line tables, target headers, and final MIPS instruction encodings.

Key behavior:
- Provides endian-aware output macros and `objput`/`objhput`/`lput`, switching target long/halfword byte order through the global `little`.
- `asmb` emits text instructions, string constants, data blocks, optional symbols/line tables, then rewinds to write one of several supported executable headers: Unix ECOFF-like, Plan 9, SGI COFF, ELF, or headerless.
- `asmsym` and `putsymb` emit Plan 9 symbol records for text, leaf text, data, bss, string constants, file history, frames, autos, and params.
- `asmlc` emits compressed line-number deltas.
- `datblk` materializes initialized data/string bytes, detects duplicate initialization, and handles integer, string, and floating constants with host/target byte-order maps.
- `asmout` maps `Optab.type` templates to concrete MIPS words, including synthetic multiword sequences for large constants, long memory references, FP loads/stores, case tables, jump delay-slot folding, LL/SC, HI/LO, CP0, and FP control registers.
- `oprrr`, `opirr`, and `vshift` encode the instruction format constants used by `asmout`.

Integration and risks:
- Relies on `span.c`/`optab.c` to classify operands and choose instruction templates before emission.
- Header generation is strongly tied to `HEADTYPE`, `INITTEXT`, `INITDAT`, `INITRND`, and `entryvalue`.
- Several paths assume fixed MIPS instruction widths and Plan 9 symbol encoding; changing `Optab.type` values requires matching `asmout`.
