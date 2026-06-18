# File Research: sources/os/plan9/plan9/sys/src/9/bcm/vfp3.c

This file is a one-line wrapper including `../teg2/vfp3.c`.

It reuses Tegra VFPv3 support for the BCM build.

Integration points: provides hardware VFP functions declared in `fns.h`, working with `FPsave` in `dat.h` and undefined-instruction/FPU trap logic.

Risk notes: actual VFP register handling and CPU feature probing are in the included Tegra source.
