# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsbitops.c

Purpose: Implements bitmap bit/byte operations: monochrome rectangle fill, masked fill, horizontal/vertical replication, bounding-box detection, plane extraction/expansion, and byte rectangle fill/copy.

Key interfaces: `mono_copy_masks`, `mono_fill_masks`, `bits_fill_rectangle`, `bits_fill_rectangle_masked`, `bits_replicate_horizontally`, `bits_replicate_vertically`, `bits_bounding_box`, `bits_extract_plane`, `bits_expand_plane`, `bytes_fill_rectangle`, and `bytes_copy_rectangle`.

Control flow: bit fills align to machine chunks and specialize one-, two-, three-, and many-chunk spans. Replication doubles/copies bitmap rows where byte-aligned and uses bit placement otherwise. Bounding-box detection skips blank rows and scans left/right edges by longs with endian-specific bit subdivision. Plane extraction/expansion use fast cases for common CMYK-style 4-to-1 and 32-to-8 / 8-to-32 operations, otherwise fall back to generic sample load/store macros.

Dependencies: Uses Ghostscript bit tables, endian/word-size architecture macros, sample access macros from `gxbitops.h`, color-index types, and memory/string routines.

Risks and notes: Several algorithms depend on raster alignment assumptions, especially bounding-box scanning by `ulong`. Horizontal replication comments call the current algorithm inefficient. Fast paths are architecture-sensitive and need endian coverage.
