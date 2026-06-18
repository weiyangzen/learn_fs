# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/9netics64.8k/dat.h

Data/configuration header for the 9netics 64-bit, 8 KiB-block cwfs build.

It fixes `RBUFSIZE` at 8 KiB, includes `64bit.h`, sets `FIXEDSIZE = 1`, includes `portdat.h`, and declares the same two-bank memory configuration structure used by sibling builds.

The key effect is selecting the 64-bit `Off` layout and larger name/indirect-depth constants.
