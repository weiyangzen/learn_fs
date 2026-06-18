## sources/test-tools/xfstests/tests/btrfs/017

Purpose: this quick qgroup regression test checks accounting when shared extents are removed from a root and its snapshot.

Control flow: it requires scratch qgroup support and the `cloner` binary, formats btrfs with 64 KiB node size, mounts it, computes block/extent sizes, writes a direct-I/O extent to `foo`, snapshots scratch to `snap`, reflink-clones that extent into `foo-reflink` in both the root and snapshot plus a second snapshot clone, enables quotas, runs a quota rescan, removes all cloned files from both roots, syncs, and prints qgroup referenced/exclusive values.

State and persistence: scratch contains root and snapshot subvolumes, reflinked extents, qgroup metadata, and deleted extents. Output units come from `_btrfs_qgroup_units`.

Dependencies: `_require_scratch_qgroup`, `_require_cloner`, `$CLONER_PROG`, `_btrfs quota`, `_btrfs qgroup`, `$XFS_IO_PROG`, and `_filter_xfs_io_blocks_modified`.

Risks: qgroup output format and units depend on btrfs-progs helpers. The test primarily looks for warnings/accounting regressions, so exact numeric output is filtered but still version-sensitive. Requires reflink support through cloner.

Test signals: no warning/crash and stable qgroup output after deletions. Unexpected qgroup accounting or dmesg warnings indicate the targeted regression.
