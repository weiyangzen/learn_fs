# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/riva_tbl.h

Static NVIDIA RIVA initialization table header, copied from NVIDIA/XFree86-era sources.

Contents:
- Copyright/license notice from NVIDIA and XFree86 revision marker.
- Common fixed-function tables:
  - `RivaTablePMC`
  - `RivaTablePTIMER`
  - `RivaTableFIFO`
- NV3 tables:
  - PFIFO, PGRAPH, PGRAPH depth variants for 8/15/32 bpp, PRAMIN, PRAMIN depth variants.
- NV4 tables:
  - FIFO, PFIFO, PGRAPH, PGRAPH depth variants for 8/15/16/32 bpp, PRAMIN, PRAMIN depth variants.
- NV10 tables:
  - FIFO, PFIFO, PGRAPH, PGRAPH depth variants for 8/15/16/32 bpp, `nv10tri05TablePGRAPH`, PRAMIN, PRAMIN depth variants.

Behavior:
- No functions or control flow.
- Provides register/value pairs consumed by NVIDIA/RIVA driver code elsewhere.
- Depth-specific tables adjust graphics object and PRAMIN format state for color layout.

Filesystem relevance:
- Indirect: static display hardware initialization data, not storage code.
