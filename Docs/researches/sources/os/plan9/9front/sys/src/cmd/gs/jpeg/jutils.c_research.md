# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jutils.c

Purpose: shared JPEG library utility tables and small helper routines used by compression and decompression.

Key contents:
- Defines `JPEG_INTERNALS`, includes `jinclude.h` and `jpeglib.h`.
- Disabled `jpeg_zigzag_order` table under `#if 0`.
- Active `jpeg_natural_order[DCTSIZE2+16]` table maps zigzag positions to natural DCT block positions.
- Arithmetic helpers: `jdiv_round_up()` and `jround_up()`.
- FAR-memory aware copy/zero helpers: `jcopy_sample_rows()`, `jcopy_block_row()`, `jzero_far()`.

Important behavior:
- `jpeg_natural_order` includes 16 extra entries set to 63 to contain out-of-range coefficient writes from corrupted entropy data without adding an inner-loop bounds check.
- FAR pointer handling supports old segmented-memory DOS compilers; normal builds map to `MEMCOPY` and `MEMZERO`.
- Sample row copying allows overlapping source/destination rows for row duplication.
- Block row copying moves coefficient blocks as raw `JCOEF` sequences when far-memory bulk copy is unavailable.

Dependencies:
- Memory macros from `jinclude.h`, JPEG sample/coefficient types from `jpeglib.h`.
