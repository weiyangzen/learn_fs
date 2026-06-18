# File Research: sources/os/plan9/plan9/sys/src/9/bcm/mouse.c

This file is a one-line wrapper including `../omap/mouse.c`.

It reuses OMAP mouse support for the BCM build, while BCM-specific display cursor drawing is implemented in `screen.c`.

Integration points: interacts with `screen.h` functions such as `mousexy`, `setcursor`, and `cursoron/off`.

Risk notes: actual mouse device behavior is in the included OMAP source.
