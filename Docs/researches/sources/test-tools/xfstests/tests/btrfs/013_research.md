## sources/test-tools/xfstests/tests/btrfs/013

Purpose: this quick balance/prealloc regression test ensures balancing a preallocated extent with checksummed data does not produce missing or failed checksum reports.

Control flow: it records current dmesg counts for `no csum found` and `csum failed`, creates a preallocated 1 MiB file with an 8 KiB write at 16 KiB, runs a btrfs balance, remounts scratch, reads the file back, and checks dmesg counts did not increase.

State and persistence: scratch contains `foo`; dmesg is read before and after. `$seqres.full` captures xfs_io and balance logs.

Dependencies: `_require_scratch`, `_require_xfs_io_command "falloc"`, `$XFS_IO_PROG`, `_run_btrfs_balance_start`, `_scratch_unmount`, `_scratch_mount`, and `dmesg`.

Risks: dmesg count comparison is global to the host and can be affected by unrelated btrfs activity. It relies on exact kernel log substrings. It reads post-remount to force checksum validation.

Test signals: expected output is `Silence is golden`. A pread error or increased checksum log count triggers `_fail`.
