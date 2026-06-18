# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/emelie/dat.h

Build-time data layout header for the Emelie variant.

Key responsibilities:
- Defines `RBUFSIZE` as 16K.
- Includes `32bit.h`.
- Sets `FIXEDSIZE = 1`.
- Includes shared `portdat.h`.
- Defines `Mbank`/`Mconf` fake memory-bank structures and `extern Mconf mconf`.

Research notes:
- Structurally matches `cwfs/dat.h`; behavioral differences are in `emelie/conf.c`.
