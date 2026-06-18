# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/mach64.c

Implements a simple ATI Mach64 path similar to `mach32.c`, with fixed-clock table assumptions rather than full programmable support. It initializes ATI extended-register access, saves selected extended registers and 32-bit config/memory/scratch registers, and derives memory size from `Memcntl`.

`init` assumes the ATI18818 clock table, finds a clock within 1 MHz with optional divide-by-two, configures 8-bit VGA register state, sets clock bits, handles interlace, disables the 128 KB CPU aperture bit, sets `ctlr->type` to `mach32`, and clamps VGA-mode visible memory to 1 MB.

`load` writes selected extended registers and `MiscW`. More complete Mach64-family support is in `mach64xx.c`.
