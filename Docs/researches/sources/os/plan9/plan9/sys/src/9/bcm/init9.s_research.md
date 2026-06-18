# File Research: sources/os/plan9/plan9/sys/src/9/bcm/init9.s

This file is a one-line wrapper including `../omap/init9.s`.

It reuses OMAP init assembly for the BCM build, likely for the initial user-mode bootstrap code or process entry glue.

Integration points: complements `main.c` user process creation and `touser()` path declared in `fns.h`.

Risk notes: actual behavior lives in the included OMAP file.
