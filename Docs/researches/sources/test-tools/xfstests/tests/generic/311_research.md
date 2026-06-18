# sources/test-tools/xfstests/tests/generic/311

## Purpose

Run various fsync tests with dm flakey in freeze() mode and non freeze() mode. The idea is that we do random writes and randomly fsync and verify that after a fsync() followed by a freeze()+failure or just failure that the file is correct. We remount the file system after the failure so that the file system can do whatever cleanup it needs to and md5sum the file to make sure it matches hat it was before the failure. We also fsck to make sure the file system is consistent The fsync tester just random writes into prealloc or not, and then fsync()s randomly or sync()'s randomly and then fsync()'s before exit. There are a few tests that were handcrafted to reproduce bugs in btrfs, so it's also a regression test of sorts. It is registered with `_begin_fstest auto metadata log prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `311` plus `_begin_fstest auto metadata log prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`. Capability gates: `_require_scratch_nocheck`, `_require_odirect`, `_require_dm_target flakey`, `_require_xfs_io_command "falloc"`, `_require_test_program "fsync-tester"`, `_require_metadata_journaling $SCRATCH_DEV`. Local functions: `_cleanup`, `_run_test`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 43: `SEED=1`
- Line 44: `testfile=$SCRATCH_MNT/$seq.fsync`
- Line 49: `test_num=$1`
- Line 51: `direct_opt=""`
- Line 81: `buffered=0`
- Line 82: `direct=1`
- Line 85: `lockfs=1`
- Line 86: `SEED=$i`

## Control Flow

The visible phases are driven by echo markers such as line 87 `echo "Running test $i buffered, normal suspend"`, line 89 `echo "Running test $i direct, normal suspend"`, line 93 `echo "Running test $i buffered, nolockfs"`, line 95 `echo "Running test $i direct, nolockfs"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 33: `_require_scratch_nocheck`
- Line 35: `_require_dm_target flakey`
- Line 39: `_require_xfs_io_command "falloc"`
- Line 41: `_require_test_program "fsync-tester"`
- Line 44: `testfile=$SCRATCH_MNT/$seq.fsync`
- Line 46: `_run_test()`
- Line 54: `$here/src/fsync-tester -s $SEED -t $test_num $direct_opt $testfile`
- Line 55: `[ $? -ne 0 ] && _fatal "fsync tester exited abnormally"`
- Line 59: `_scratch_unmount`
- Line 63: `_scratch_mount`
- Line 67: `_scratch_unmount`
- Line 68: `_check_scratch_fs`
- Line 71: `_scratch_mount`
- Line 96: `_run_test $i $direct`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. dm-flakey is used to simulate a dropped write / power-fail boundary and then remount for recovery checks. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `metadata`, `log`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`, and uses capability gates such as `_require_scratch_nocheck`, `_require_odirect`, `_require_dm_target flakey`, `_require_xfs_io_command "falloc"`, `_require_test_program "fsync-tester"`, `_require_metadata_journaling $SCRATCH_DEV`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Crash-recovery tests require dm-flakey behavior and metadata journaling; failures can appear as lost directory entries, stale content, or mount-time recovery errors.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
