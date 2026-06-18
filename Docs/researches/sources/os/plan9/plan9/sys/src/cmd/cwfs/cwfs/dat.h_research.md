# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/cwfs/dat.h

Build-time data layout header for the generic old-cw variant.

Key responsibilities:
- Defines `RBUFSIZE` as `16*1024` unless already defined.
- Includes `32bit.h`, selecting 32-bit on-disk/address layout.
- Sets `FIXEDSIZE = 1`, assuming jukebox discs are uniform size.
- Includes shared `portdat.h`.
- Defines user-mode fake memory-bank structures:
  - `MAXBANK = 2`
  - `Mbank`
  - `Mconf`
  - external `mconf`.

Research notes:
- The comments emphasize `RBUFSIZE` cannot be runtime-variable because it shapes on-disk arrays such as freelist blocks.
