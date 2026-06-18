## sources/test-tools/xfstests/tests/btrfs/025

Purpose: this quick send/clone/prealloc regression test ensures incremental send does not emit unaligned clone operations that make receive fail.

Control flow: it creates `foo`, truncates and preallocates ranges, writes a short unaligned range, snapshots as `mysnap1`, truncates to a different unaligned size, snapshots as `mysnap2`, sends full and incremental streams to `$tmp`, records md5s for live and snapshot files, checks the filesystem, reformats scratch, receives both streams, and records md5s for received snapshots.

State and persistence: temporary send streams live in a `mktemp -d` directory. Scratch is reformatted between send and receive phases. Snapshots `mysnap1` and `mysnap2` preserve the tested file states.

Dependencies: `_require_scratch`, `_require_xfs_io_command "falloc"`, `$XFS_IO_PROG`, `_btrfs filesystem sync`, `_btrfs subvolume snapshot`, `_btrfs send/receive`, `_check_btrfs_filesystem`, and `_filter_scratch`.

Risks: md5 output is path-filtered but not compared programmatically; golden output is the oracle. The test targets precise unaligned offsets and lengths, so changing them could miss the bug. It overrides `tmp` with a directory and cleanup removes it.

Test signals: receive must succeed for both streams, filesystem checks must pass before and after receive, and md5 output should match expected golden values.
