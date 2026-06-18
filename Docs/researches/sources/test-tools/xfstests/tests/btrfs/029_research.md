## sources/test-tools/xfstests/tests/btrfs/029

Purpose: this quick clone test verifies reflink behavior across different filesystems and across different mountpoints of the same btrfs filesystem.

Control flow: it requires test, scratch, and `cp --reflink` support, creates a test output directory, formats and mounts scratch, writes an original file, tests copying from scratch to test filesystem with `--reflink=auto` and `--reflink=always`, then bind/mounts the scratch device at the test directory and repeats `--reflink=auto` and `--reflink=always` between two mountpoints of the same filesystem. It unmounts the extra mountpoint at the end.

State and persistence: scratch contains `original`; `TEST_DIR/test-$seq` contains copy targets and temporarily becomes a second mountpoint for `SCRATCH_DEV`.

Dependencies: `common/reflink`, `_require_cp_reflink`, `$XFS_IO_PROG`, `cp`, `_mount`, `$UMOUNT_PROG`, `_filter_testdir_and_scratch`, and `md5sum`.

Risks: comments say same-filesystem `--reflink=always` should succeed, but an in-code comment before that command still says "should fail outright"; the actual md5 check expects a copy to exist. Extra mount cleanup is manual via `$UMOUNT_PROG`, not `_unmount`. Coreutils versions differ in whether a failed destination file is created, so `ls` output is logged only to `$seqres.full`.

Test signals: different-device `--reflink=auto` should produce identical md5s via fallback, different-device `--reflink=always` should print `cp reflink failed`, and same-device different-mountpoint auto/always copies should yield matching md5s.
