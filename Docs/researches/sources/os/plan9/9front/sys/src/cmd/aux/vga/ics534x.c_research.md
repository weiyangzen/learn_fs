# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/ics534x.c

Implements ICS534x GENDAC support for ET4000-W32p and ARK2000pv pairings. It toggles board-specific RS2 access through either CRTC `0x31` or sequencer `0x1C`, and errors if used with an unsupported controller.

`options` advertises 2x8 pixel-clock support. `init` derives speed grade from name, validates pclk, may halve pclk and resync for 2x8 mode, and either selects standard VGA clocks or brute-forces GENDAC PLL `M/N/R`.

`load` enters snooze/color mode, writes PLL f7 parameters when needed while preserving memory-clock control, sets pixel mode, restores RS2, and marks loaded. `dump` prints all PLL slots and decoded frequencies.
