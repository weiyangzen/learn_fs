## sources/test-tools/xfstests/tests/btrfs/024

Purpose: this quick compression regression test checks that setting a file compression flag while filesystem compression is disabled does not oops when writing data.

Important local API: `__workout` creates `tmpfile`, applies `chattr =c`, writes 1 MiB with xfs_io, and filters xfs_io output.

Control flow: it requires scratch and that btrfs is not mounted with nodatacow, then runs the workout on a filesystem mounted with `compress=no`, unmounts and checks scratch, then repeats with `compress-force=no`.

State and persistence: scratch is reformatted twice and contains `tmpfile` in each run. File attributes are mutated by `chattr`.

Dependencies: `_require_btrfs_no_nodatacow`, `$CHATTR_PROG`, `$XFS_IO_PROG`, `_filter_xfs_io`, `_scratch_mkfs`, `_scratch_mount`, `_scratch_unmount`, and `_check_scratch_fs`.

Risks: the command `$CHATTR_PROG =c` depends on btrfs chattr syntax for setting compression attribute. The second run does not call `_check_scratch_fs` after unmount, relying on framework behavior or prior checks.

Test signals: headings `*** test compress=no`, `*** test compress-force=no`, and `*** done`; failures are write errors, fs check failures, or kernel crashes/oopses.
