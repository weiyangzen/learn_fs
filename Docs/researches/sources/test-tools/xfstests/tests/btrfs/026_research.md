## sources/test-tools/xfstests/tests/btrfs/026

Purpose: this quick compression/preallocation regression test verifies direct I/O writes spanning preallocated and compressed extents complete correctly and persist across remount.

Control flow: it formats and mounts scratch with compression, creates a compressed extent in `foo` at 700K-800K, preallocates 600K-700K, writes 80K direct I/O across 640K-720K, then creates a large `bar` case with a 128M compressed extent, preallocation to 258M, and a 256M direct I/O write from 3M. It prints md5s for both files before and after `_scratch_cycle_mount`.

State and persistence: scratch contains `foo` and `bar` with mixed compressed, preallocated, direct, and buffered data. The remount checks persistence and page-cache independence.

Dependencies: `_require_xfs_io_command "falloc"`, `$XFS_IO_PROG`, `_filter_xfs_io`, `_scratch_mkfs`, `_scratch_mount "-o compress"`, `_scratch_cycle_mount`, and `md5sum`.

Risks: large writes require significant scratch space and time. The expected data ranges are documented in comments but validated only by md5 golden output. Compression behavior can vary by kernel/progs/mount options but the fixed byte patterns should force the intended extent types.

Test signals: stable md5s before and after remount and no direct I/O/writeback assertion or command failure.
