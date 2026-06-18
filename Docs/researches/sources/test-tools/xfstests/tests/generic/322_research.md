# sources/test-tools/xfstests/tests/generic/322

## Purpose

Runs various rename fsync tests to cover some rename fsync corner cases Btrfs wasn't making sure the new file after rename survived the fsync. It is registered with `_begin_fstest auto quick metadata log` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `322` plus `_begin_fstest auto quick metadata log`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`. Capability gates: `_require_scratch_nocheck`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local functions: `_cleanup`, `_clean_working_dir`, `_rename_test`, `_write_after_fsync_rename_test`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 79: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 35 `echo "fsync rename test"`, line 55 `echo "fsync rename test"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 22: `_require_scratch_nocheck`
- Line 27: `_scratch_mount`
- Line 29: `_scratch_unmount`
- Line 35: `echo "fsync rename test"`
- Line 37: `$XFS_IO_PROG -f -c "pwrite 0 1M" -c "fsync" $SCRATCH_MNT/foo \`
- Line 40: `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/bar`
- Line 43: `_flakey_drop_and_remount`
- Line 46: `_scratch_unmount`
- Line 53: `_write_after_fsync_rename_test()`
- Line 56: `_scratch_mount`
- Line 58: `-c "sync_range -b 2M 1M" $SCRATCH_MNT/foo >> $seqres.full 2>&1`
- Line 60: `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/bar`
- Line 63: `_flakey_drop_and_remount`
- Line 77: `_write_after_fsync_rename_test`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. dm-flakey is used to simulate a dropped write / power-fail boundary and then remount for recovery checks. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `metadata`, `log`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`, and uses capability gates such as `_require_scratch_nocheck`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Crash-recovery tests require dm-flakey behavior and metadata journaling; failures can appear as lost directory entries, stale content, or mount-time recovery errors.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
