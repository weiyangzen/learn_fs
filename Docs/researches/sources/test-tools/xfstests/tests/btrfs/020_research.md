## sources/test-tools/xfstests/tests/btrfs/020

Purpose: this quick replace/volume regression test verifies btrfs refuses device replace on a read-only mounted filesystem.

Control flow: it requires a three-device scratch pool, records the kernel commit hint for the fix, takes two devices plus a spare, formats RAID1 data/metadata, mounts scratch read-only, runs `btrfs replace start -B 2 $SPARE_DEV $SCRATCH_MNT`, filters blank lines and scratch paths from the expected failure output, unmounts, and releases the spare/pool.

State and persistence: scratch pool devices are formatted as RAID1; no successful replace should occur. `SPARE_DEV` and scratch pool globals are restored.

Dependencies: `_require_scratch_dev_pool`, `_scratch_dev_pool_get`, `_spare_dev_get`, `_scratch_pool_mkfs`, `_scratch_mount -o ro`, `$BTRFS_UTIL_PROG replace`, and `_filter_scratch`.

Risks: the replace command is expected to fail, but the script does not explicitly assert nonzero return; golden output must reflect the failure message. Device id `2` assumes btrfs device numbering after mkfs.

Test signals: stable filtered error output is expected. A silent successful replace or changed error message can produce golden output differences.
