# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmgr.h

Shared MGR device definitions.

- Declares MGR 8-bit color mapping procs used by `gdevmgr.c`.
- Defines MGR bitmap header encoding macro `B_PUTHDR8` and `struct b_header`.
- Defines `struct nclut` for color lookup table entries.
- Provides constants for MGR LUT types, RGB channels, and 16-entry palette ramps.
- Contains static `mgrlut[LUT][RGB][LUTENTRIES]` with built-in black/white, gray, biased gray, VGA, BCT, and user palettes.
- Integration role: shared header for MGR output format structure and palette definitions.
