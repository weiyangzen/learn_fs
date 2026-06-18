# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/3dfx.c

`3dfx.c` is a VGA controller module for 3Dfx Banshee, Voodoo3, and Voodoo5 devices. It locates PCI vendor `0x121A`, maps I/O register BAR 2, records up to 0x100 bytes of MMIO-style registers via port I/O, determines max PLL frequency and framebuffer size, and configures display mode registers.

It computes PLL parameters from reference frequency using m/n/p ranges, supports standard VGA clocks and programmed PLL clocks, and uses two-pixels-per-clock mode above 135 MHz when allowed and mode width is divisible by 16.

Mode setup programs screen size, stride, pixel format for 8/16/32 bpp, DAC mode, video processor config, VGA init, CRT overflow bits, and black attribute entry. `load` writes extended CRT registers and 3Dfx registers; `dump` prints captured registers and PLL-derived frequencies.

It exposes `Ctlr tdfx` and a placeholder `tdfxhwgc`.
