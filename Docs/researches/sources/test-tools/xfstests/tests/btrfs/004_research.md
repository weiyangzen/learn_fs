## sources/test-tools/xfstests/tests/btrfs/004

Purpose: this metadata/fiemap test validates btrfs backreference walking by mapping file extents to physical addresses and resolving them back to the expected inode and path inside a snapshot.

Important local APIs: `_filter_extents` parses `filefrag -v` into `physical#length#logical#flags`. `_check_file_extents` logs and returns parsed extents. `_btrfs_inspect_addr` uses `btrfs inspect-internal logical-resolve` and checks the expected inode, logical offset, and root. `_btrfs_inspect_inum` uses `inode-resolve` to check the path. `_btrfs_inspect_check` combines `stat`, logical resolve, and inode resolve. `workout` drives the filesystem workload.

Control flow: it formats a 2 GiB scratch filesystem, runs write-heavy fsstress, snapshots it, remounts with compression, runs metadata noise, remounts with atime, optionally starts background fsstress noise, then samples files from the snapshot and validates every non-inline extent through btrfs backref resolution.

State and persistence: scratch contains random fsstress trees, snapshot `snap1`, a `next` directory, and transient `bgnoise`. `$tmp.running` controls the background noise loop. Diagnostics are appended to `$seqres.full`.

Dependencies: `filefrag`, `btrfs inspect-internal logical-resolve`, `inode-resolve`, fsstress, `_scratch_mkfs_sized`, `_run_fsstress`, `_btrfs`, and generic filters.

Risks: sampling files with `shuf` introduces runtime variability, though output is mostly diagnostic. Inline extents are skipped because logical-resolve cannot map them. Background noise increases race coverage but can make failures timing-dependent. The cleanup `rm $tmp.running` can complain if the file is already gone.

Test signals: stdout should show `*** test backref walking` and `*** done`. Any unexpected logical/inode resolve output or accumulated extent errors triggers `_fail`.
