# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/fs64/dat.h

Build-time data layout header for the `fs64` variant.

Key responsibilities:
- Defines `RBUFSIZE` as 8K.
- Includes `64bit.h`, selecting 64-bit on-disk/address layout.
- Sets `FIXEDSIZE = 1`.
- Includes shared `portdat.h`.
- Defines fake memory-bank structures `Mbank` and `Mconf`.

Research notes:
- The combination of 8K blocks and 64-bit offsets changes both maximum file size and protocol compatibility.
