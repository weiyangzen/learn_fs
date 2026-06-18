# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/ldecomp.s

## Purpose
Real-mode assembly entry for the decompressor image, loaded at `0x10000` or `0x7c00`, that prepares basic BIOS data and switches to protected mode before calling `_main`.

## Main Interfaces
- Entry symbol `origin`.
- Provides `_cgaputs`, `outb`, `inb`, `mb586`, `wbinvd`, and `splhi`.

## Implementation Notes
- Disables interrupts, normalizes DS/SS, sets stack at the origin, enables A20 through BIOS, and forces CGA mode 3.
- Prints `9boot ` using BIOS INT 10h.
- Writes APM and E820 records to `BIOSTABLES`, mirroring the full real-mode startup path.
- Loads a simple GDT, sets protected mode with LMSW encoding, loads segment selectors, sets a high stack, and far-jumps to `_main`.
- Defines a minimal GDT with data, 32-bit code, and 16-bit code descriptors.

## Dependencies And Risks
- Uses manual opcode bytes for protected-mode transition instructions.
- BIOS table layout must match `conf.c` parsing.
- This is decompressor-specific and deliberately smaller than the full boot runtime.
