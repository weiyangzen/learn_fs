# File Research: sources/local-fs/xfsprogs/db/freesp.c

## Purpose
Implements the `xfs_db freesp` command, which scans allocation group free-space metadata and reports free extents as a histogram, summary, or raw dump.

## Main Interfaces
- Registers `freesp` through `freesp_init()`.
- Command options select AGs (`-a`), alignment filtering (`-A`), count-btree scan (`-c`), raw extent dump (`-d`), summary (`-s`), and histogram bucket strategy (`-b`, `-e`, `-h`, `-m`).
- Uses `libfrog/histogram` for bucket creation, accumulation, printing, and summary output.

## Control Flow
`freesp_f()` parses options via `init()`, scans every selected AG, prints the histogram and optional summary, and frees temporary state. `scan_ag()` reads the AGF, counts AGFL blocks through `libxfs_agfl_walk`, then scans either the by-block-number or by-count free-space btree. Leaf records add extents to the histogram; interior records recursively read child btree blocks.

## Dependencies
Depends on global xfs_db state (`mp`, `blkbb`, `iocur_top`), IO cursor helpers from `io.c`, type descriptors for AGF/AGFL/BNOBT/CNTBT, and libxfs allocation-btree layout macros.

## Risks And Invariants
- Free extents are trusted after minimal magic checks; corrupt btree record counts or pointers can truncate output rather than diagnose all corruption.
- AGFL scan first validates `agf_flfirst` and `agf_fllast` against `libxfs_agfl_size`.
- `-A` filters on filesystem block number modulo alignment, not AG-relative block number.
