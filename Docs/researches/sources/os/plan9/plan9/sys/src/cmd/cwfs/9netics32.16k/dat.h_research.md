# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/9netics32.16k/dat.h

Data/configuration header for the 9netics 32-bit, 16 KiB-block cwfs build.

It fixes `RBUFSIZE` at 16 KiB, includes `32bit.h`, sets `FIXEDSIZE = 1`, includes shared `portdat.h`, and declares a small physical memory configuration structure with two memory banks.

This header chooses the on-disk format and raw buffer size for the build.
