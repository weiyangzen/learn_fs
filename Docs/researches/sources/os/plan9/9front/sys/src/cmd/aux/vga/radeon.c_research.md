# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/radeon.c

Plan 9 `aux/vga` controller for ATI Radeon R100/R200/R300-era cards. It maps Radeon MMIO, reads BIOS PLL parameters, computes CRTC timing and pixel PLL registers, programs CRT output, and initializes palette/gamma for true-color modes.

Key behavior:
- `Radeon` private state stores MMIO base, PCI device, BIOS bytes, framebuffer size, display type, saved/common registers, CRTC timing registers, PLL limits and computed PLL values, and an R300 PLL-read workaround flag.
- Low-level helpers `OUTREG8`, `OUTREG`, `INREG`, `OUTREGP`, `OUTPLL`, `INPLL`, and `OUTPLLP` abstract MMIO and indexed PLL access.
- `radeon_getbiosparams` reads a video BIOS from `0xC0000` or `0xE0000`, validates the `0x55 0xAA` signature, and extracts reference frequency, reference divider, min/max PLL frequency, and xclk from the BIOS PLL info block.
- `radeonpci` matches ATI vendor `0x1002` against `radeon_pciids` from `radeon.h` and reports whether the device is R300.
- `snarf` disables generic VGA load hooks, maps `radeonmmio` from PCI BAR 2, reads framebuffer size, rejects non-CRT display output, reads BIOS parameters, and saves bus control.
- `radeon_init_common_registers`, `radeon_init_crtc_registers`, and `radeon_init_pll_registers` derive common disable/default state, CRTC format/timing/pitch state, and PLL reference/feedback/post-div values from the requested `Mode`.
- `load` blanks display, writes common registers, writes CRTC timing registers, performs atomic PPLL update, unblanks, and initializes a grayscale palette for modes above 8 bpp.

Notable dependencies:
- Register constants and PCI ID table from `radeon.h`.
- `readbios` from `io.c`.
- Plan 9 PCI/VGA framework functions `pcimatch`, `vgactlpci`, `vgactlw`, `segattach`, controller flags, and mode structures.

Research notes:
- Only CRT output is supported; flat panel/TMDS detection causes an error.
- BIOS parsing does not guard all failure modes beyond signature checks; if `readbios` fails unexpectedly, dereferences would be unsafe.
- PLL units are handled in 10 kHz units when `mode->frequency / 10000` is passed into `radeon_init_pll_registers`, matching the BIOS-style PLL fields.
- R300 PLL reads require a workaround read sequence after `INPLL`.
- `dump` is effectively a stub.
