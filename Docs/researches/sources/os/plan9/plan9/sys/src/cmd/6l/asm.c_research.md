# File Research: sources/os/plan9/plan9/sys/src/cmd/6l/asm.c

This file writes final amd64 linked output. `asmb` emits text, data, symbols, line tables, dynamic relocation data, and the executable header. It supports Plan 9 format (`HEADTYPE 2`) and ELF32/ELF64 (`HEADTYPE 5/6`) output.

The text pass walks `firstp`, verifies phase consistency between expected and assigned PCs, calls `asmins` for instruction encoding, flushes the output buffer, and optionally prints assembly bytes under debug. It handles dynamic-load-module relocation state while emitting text.

`datblk` builds zero-filled data blocks and overlays `ADATA` initializers, detecting overlapping initialization. It supports floating constants, string constants, integer constants, and address constants. Address constants against symbols are adjusted by symbol values and `INITDAT`; dynamic modules record relocations via `dynreloc`.

The header pass writes Plan 9 magic, text/data/bss/symbol sizes, entry value, stack pointer table size, line table size, and 64-bit entry address, or delegates to ELF writers.

Filesystem relevance is executable image construction: linked filesystem/kernel binaries depend on correct text/data layout, symbol emission, relocation, and file-format headers.
