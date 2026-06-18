## sources/test-tools/xfstests/tests/btrfs/016

Purpose: this send/prealloc regression test verifies that hole punching between two snapshots is represented correctly in incremental send/receive.

Control flow: it creates a btrfs subvolume under scratch, writes a 10 MiB file, snapshots it read-only as `snap`, punches a 1 MiB hole at offset 1 MiB in the live file, snapshots as `snap1`, records fssum manifests for both snapshots with atime and xattrs disabled, sends full and incremental streams to `$tmp`, reformats scratch, receives both streams, and verifies both received snapshots against their manifests.

State and persistence: send streams and fssum manifests are in a private temporary directory from `mktemp -d`; scratch is reformatted midway. The tested state is subvolume snapshots containing `foo` before and after hole punching.

Dependencies: `_require_fssum`, `_require_xfs_io_command "falloc"`, `$XFS_IO_PROG fpunch`, `$BTRFS_UTIL_PROG send/receive`, `_scratch_mkfs`, and `_scratch_mount`.

Risks: the script overrides `tmp` with `mktemp -d`, diverging from preamble's `$tmp` pattern and relying on the default cleanup. Xattr checks are disabled intentionally, so the signal is file data and hole layout, not metadata.

Test signals: fssum generation and restore must pass for both snapshots; send/receive failures trigger `_fail`; expected stdout is `Silence is golden`.
