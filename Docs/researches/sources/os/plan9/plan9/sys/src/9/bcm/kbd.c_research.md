# File Research: sources/os/plan9/plan9/sys/src/9/bcm/kbd.c

This file is a one-line wrapper including `../omap/kbd.c`.

It reuses OMAP keyboard support for the BCM build. On Raspberry Pi, keyboard input is generally USB-backed, but this wrapper supplies the kernel keyboard device code path.

Integration points: interacts with UART console input and USB keyboard setup through generic device layers.

Risk notes: real logic is in the included OMAP source.
