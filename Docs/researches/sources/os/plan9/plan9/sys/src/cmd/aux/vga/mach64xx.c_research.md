# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/mach64xx.c

Implements the Plan 9 `aux/vga` controller backend for ATI Mach64/Rage-family adapters.

Key behavior:
- Defines Mach64 register indices, I/O-port and PCI-register addressing tables, PLL register access, LCD indexed access, and TV indexed access.
- `snarf()` detects ATI PCI devices, selects port or PCI register access, captures core registers, PLL state, optional LCD state, memory-size encoding, aperture size, and LT panel identity.
- `clock()` computes VCLK divisors, with special handling for active LCD panels where the existing BIOS-programmed PLL is preserved.
- `setdsp()` calculates Rage display FIFO/DSP timing from BIOS memory-clock tables, memory type, panel stretch state, video frequency, and depth.
- `init()` builds Mach64 CRTC, sync, pitch, pixel-depth, overlay, PLL, linear-aperture, LCD stretch, and DSP register state.
- `load()` unlocks registers, programs aperture, timing, LCD, DAC, DSP, PLLs, pixel width, and true-color palette ramp.
- `dump()` prints register/PLL/LCD state and decodes BIOS clock/LCD tables through `dumpmach64bios()`.

Important details:
- Uses `vga->private` as `Mach64xx`, shared with the hwgc stub.
- Linear mode is supported only when requested and usable; aperture alignment is forced to 16 MB.
- Depths above 8 require PCI-style register access.
- LCD handling intentionally avoids recomputing PLL clocks and instead uses panel/BIOS-derived values.
- BIOS parsing uses raw little-endian casts from `readbios()`, with explicit comments about endian dependence.

Filesystem relevance:
- Indirect but operational: participates in configuring Plan 9’s `#v` VGA/draw device through `aux/vga`, BIOS reads, and controller hooks used before `/dev/draw` initialization.
