# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/radeon.c

Implements a Radeon `aux/vga` backend for selected ATI Radeon 7000/7200/7500/8500/9000/9500/9700-era adapters.

Key behavior:
- Defines `Radeon` state for MMIO, PCI device, BIOS data, framebuffer size, display type, common display registers, CRTC timing, PLL programming, and R300 workaround state.
- Provides MMIO and PLL access helpers: `OUTREG`, `INREG`, `OUTREGP`, `OUTPLL`, `INPLL`, and `OUTPLLP`.
- `radeon_getbiosparams()` reads ATI BIOS tables from `0xC0000` or `0xE0000` and extracts reference clock, divider, PLL min/max, and xclk.
- `radeonpci()` matches ATI PCI devices against `radeon_pciids` from `radeon.h`.
- `snarf()` disables generic VGA loading, attaches `radeonmmio`, reads framebuffer size, rejects non-CRT display paths, and captures bus/PLL state.
- `init()` initializes common registers, CRTC timings, pitch, DAC mode, and PLL values from the selected mode.
- `load()` blanks output, writes common/CRTC/PLL registers, unblanks, and initializes a grayscale palette ramp for true-color depths.

Important details:
- Flat-panel and LCD outputs are detected but rejected.
- PLL frequency input is scaled to BIOS-style units by `mode->frequency / 10000`.
- R300 chips need an additional PLL read workaround after indexed PLL access.
- `dump()` is effectively a stub.
- This backend relies heavily on register constants and PCI ID tables in `radeon.h`.

Filesystem relevance:
- Uses `#v/vgactl` and `segattach("radeonmmio")`; it configures Plan 9 video devices through the device namespace.
