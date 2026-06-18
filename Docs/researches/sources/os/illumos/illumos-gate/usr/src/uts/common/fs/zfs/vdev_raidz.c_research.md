# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_raidz.c

## Purpose
Implements RAID-Z vdev mapping, parity generation, reconstruction, read/write dispatch, checksum/parity verification, repair, dump I/O, resilver decisions, translation, and vdev ops registration. It supports single, double, and triple parity using GF(2^8) Reed-Solomon style coding.

## RAID-Z Layout And Math
- Parity columns are P, Q, and R. P is XOR parity; Q uses powers of 2; R uses powers of 4.
- `vdev_raidz_map_alloc()` maps a logical zio into columns, sizes, device indexes, offsets, parity/data counts, skipped sectors, and ABD slices.
- Short columns are treated as zero-filled during parity generation and reconstruction.
- A historical single-parity parity rotation based on bit 20 of logical offset is preserved as an on-disk format requirement.

## Main Structures
- `raidz_map_t` holds accessed columns, skipped columns, parity count, missing data/parity counts, ABD copy for reports, error-injection flag, ops pointer, and variable `raidz_col_t` array.
- `raidz_col_t` records child index, child offset, size, ABD, generated-good-data ABD, and I/O state/error flags.

## Key Mapping And Lifetime Functions
- `vdev_raidz_map_alloc()` calculates sector quotient/remainder, big columns, accessed/skipped columns, total asize, per-column child offsets, ABDs for parity and data, optional skip padding, and selected math ops.
- `vdev_raidz_map_free()` releases parity ABDs, data ABD references, generated data, and any checksum-copy ABD.
- `vdev_raidz_vsd_ops` wires map lifetime and checksum reporting into zio VSD handling.
- Checksum reporting keeps a copy of read data so later ereport finalization can compare bad disk data to the reconstructed good data.

## Parity Generation
- Scalar fallback functions generate P, PQ, or PQR parity using ABD iteration and 64-bit GF multiply helpers.
- `vdev_raidz_generate_parity()` first tries the selected RAID-Z math backend via `vdev_raidz_math_generate()` and falls back to original scalar implementations when the backend returns `RAIDZ_ORIGINAL_IMPL`.

## Reconstruction
- Optimized scalar special cases handle one missing data column via P or Q and two missing data columns via P+Q.
- `vdev_raidz_reconstruct()` classifies targeted and errored columns into bad parity and bad data, asks the math backend for reconstruction, tries optimized scalar paths, then falls back to general matrix reconstruction.
- General reconstruction builds selected Vandermonde/identity rows, removes failed rows, inverts the needed matrix rows using Gauss-Jordan elimination in GF(2^8), and reconstructs missing data columns.
- Nonlinear/scatter ABDs are converted to temporary linear ABDs for the matrix path, then copied back.
- `vdev_raidz_combrec()` attempts combinatorial reconstruction over possible bad columns after all columns have been read but checksum still fails, identifying silent corruption candidates.

## I/O Flow
- `vdev_raidz_open()` validates parity count and child count, opens children, computes aggregate size and max size from the minimum child sizes, and fails if open errors exceed parity.
- `vdev_raidz_io_start()` allocates the map. Writes generate parity, issue children for all accessed data/parity columns, and issue optional NODATA writes for skipped sectors to improve aggregation. Reads issue data-column reads by default and include parity reads when scrub/resilver or missing data requires it.
- `vdev_raidz_io_done()` accepts writes if failures do not exceed parity. Reads proceed through phases: verify checksum with available data, reconstruct known data failures, read all columns if needed, attempt combinatorial reconstruction, then either mark checksum verified or fail with `ECKSUM`/worst I/O error.
- On successful reads with unexpected errors or resilver flags, bad/stale columns are repaired with async write child I/Os and `IO_REPAIR`, optionally `SELF_HEAL`.
- `raidz_parity_verify()` regenerates parity and compares it with parity columns that were actually read, posting checksum errors for parity mismatches unless parity checksums are disabled with `ZIO_CHECKSUM_NOPARITY`.

## Dump I/O
`vdev_raidz_dumpio()` handles dump devices specially under `_KERNEL`: it maps a full 128 KiB logical block but reads/writes only the requested data-column portions and deliberately avoids parity for dump performance and simplicity.

## Resilver, State, And Translation
- `vdev_raidz_state_change()` faults the vdev when faulted children exceed parity, degrades it for any degraded/faulted child otherwise, and marks healthy with no child issues.
- `vdev_raidz_need_resilver()` returns true for full-width stripes or if any touched child has a nonempty partial DTL.
- `vdev_raidz_xlate()` translates a logical parent range to a child range by row/column math for leaf-level physical work such as initialization.

## Registered Ops
`vdev_raidz_ops` provides open/close/asize/io_start/io_done/state_change/need_resilver/xlate/dumpio and marks RAID-Z as a non-leaf vdev type.
