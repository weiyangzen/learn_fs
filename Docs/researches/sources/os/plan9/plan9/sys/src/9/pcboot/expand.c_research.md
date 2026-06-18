# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/expand.c

## Purpose
Tiny decompressor/launcher that expands a gzipped boot loader appended after its data segment and transfers control to the protected-mode loader.

## Main Interfaces
- Entry `_main()`.
- Provides tiny runtime helpers `malloc`, `free`, `puts`, `print`, and `exits`.
- Provides A20 helpers `i8042a20`, `a20init`.
- Uses `gunzip` from included `inflate.guts.c`.

## Implementation Notes
- Copies appended payload from `edata` to `Bootkernaddr`, clears BSS, initializes CGA output, and optionally decompresses gzip data from `Unzipbuf`.
- Validates Plan 9 exec magic (`I_MAGIC` or `S_MAGIC`) after byte swapping.
- `run` aligns the data segment to page boundary, prints entry, and calls the entry directly.
- A20 detection writes test values at `0` and `1MB`; enable path first tries keyboard controller command `0xD1`, then system control port A.
- Implements a minimal `%x`, `%p`, `%d`, `%s` formatter over CGA.

## Dependencies And Risks
- Assumes fixed boot memory layout from `mem.h`.
- `malloc` is a bump allocator with no free.
- If A20 cannot be enabled, it prints and spins forever.
