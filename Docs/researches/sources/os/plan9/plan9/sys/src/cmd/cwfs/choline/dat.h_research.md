# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/choline/dat.h

Data/configuration header for the `choline` cwfs build.

It fixes `RBUFSIZE` at 16 KiB, includes `32bit.h`, sets `FIXEDSIZE = 1`, includes shared `portdat.h`, and declares the same two-bank memory configuration structure used by other 32-bit cwfs profiles.

This selects old 32-bit disk compatibility while allowing both 9P1 and 9P2000 service in `conf.c`.
