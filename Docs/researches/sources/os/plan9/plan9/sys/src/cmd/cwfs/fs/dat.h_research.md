# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/fs/dat.h

Build-time data layout header for the `fs` variant.

Key responsibilities:
- Defines `RBUFSIZE` as 4K.
- Includes `32bit.h`.
- Sets `FIXEDSIZE = 1`.
- Includes shared `portdat.h`.
- Defines fake memory-bank structures `Mbank` and `Mconf`.

Research notes:
- This 4K block size changes all derived on-disk constants in `portdat.h`, including directory entries per block and indirect fanout.
