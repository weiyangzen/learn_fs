## sources/test-tools/xfstests/tests/btrfs/021

Purpose: this quick balance/defrag regression test races balance against snapshot-aware defragmentation writeback to catch a historical crash path.

Important local API: `run_test` starts `_run_btrfs_balance_start` in the background, sleeps briefly, defragments all files found under scratch with `btrfs filesystem defrag -f`, syncs, and waits for balance completion.

Control flow: it formats and mounts scratch, creates 101 padding files to increase btree height, creates 51 fragmented files by writing 20 blocks backward with direct I/O, syncs metadata to disk, then runs the balance/defrag race.

State and persistence: scratch contains padding files and fragmented `foo-*` files. `$seqres.full` captures xfs_io and balance logs.

Dependencies: `_require_scratch`, `_scratch_mkfs`, `_scratch_mount`, `$XFS_IO_PROG`, `_filter_xfs_io`, `$BTRFS_UTIL_PROG filesystem defrag`, `find`, `xargs`, and `_run_btrfs_balance_start`.

Risks: race coverage depends on timing (`sleep 0.5`) and filesystem/device speed. Newer btrfs-progs defrag path output is redirected to `/dev/null` to avoid golden changes. No explicit content check is performed.

Test signals: success prints `Silence is golden`; crashes, command failures, dmesg warnings, or balance/defrag failures indicate regression.
