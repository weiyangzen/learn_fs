# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/9netics32.16k/dat.h

Build configuration header for 9netics 32-bit, 16K-block cwfs.

Important details:
- Defines `RBUFSIZE` as `16*1024` unless already supplied.
- Includes `32bit.h`.
- Sets `FIXEDSIZE=1`, assuming equal-sized optical media.
- Includes common `portdat.h`.
