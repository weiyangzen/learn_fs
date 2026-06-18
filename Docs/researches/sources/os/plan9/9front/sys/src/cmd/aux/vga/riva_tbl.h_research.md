# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/riva_tbl.h

NVIDIA RIVA fixed-function initialization table header derived from old NVIDIA/XFree86 sources. It contains static address/value tables for initializing PMC, PTIMER, FIFO/PFIFO, PGRAPH, and PRAMIN state across NV3, NV4, and NV10 generations, including depth-specific table variants.

Key contents:
- Common `RivaTablePMC`, `RivaTablePTIMER`, and `RivaTableFIFO` tables.
- NV3 tables for PFIFO, PGRAPH, PGRAPH depth variants for 8/15/32 bpp, PRAMIN, and PRAMIN depth variants.
- NV4 tables for FIFO, PFIFO, PGRAPH, PGRAPH depth variants for 8/15/16/32 bpp, PRAMIN, and PRAMIN depth variants.
- NV10 tables for FIFO, PFIFO, PGRAPH, PGRAPH depth variants, an additional `nv10tri05TablePGRAPH` table with many 3D state/register values, PRAMIN, and PRAMIN depth variants.
- Tables are simple `static unsigned[][2]` pairs, with first element being an offset/index and second element being the value to write.

Notable dependencies:
- No includes or helper macros; consumers are expected to know the target MMIO block and whether table offsets are byte offsets or already word-scaled.

Research notes:
- The header is not included by `nvidia.c` in this directory; that driver contains its own imperative initialization sequence instead.
- Because all symbols are `static`, inclusion in one or more C files would create translation-unit-local copies.
- It is data-only, so correctness depends on pairing the right table with the right architecture and color depth.
