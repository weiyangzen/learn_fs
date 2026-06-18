# sources/test-tools/xfstests/tests/generic/342

## Purpose

Test that if we rename a file, create a new file that has the old name of the other file and is a child of the same parent directory, fsync the new inode, power fail and mount the filesystem, we do not lose the first file and that file has the name it was renamed to. It is registered with `_begin_fstest auto quick metadata log` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `342` plus `_begin_fstest auto quick metadata log`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`. Capability gates: `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 68: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 51 `echo "File digests before log replay:"`, line 59 `echo "Directory a/ contents after log replay:"`, line 62 `echo "File digests after log replay:"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 20: `rm -f $tmp.*`
- Line 27: `_require_scratch`
- Line 28: `_require_dm_target flakey`
- Line 30: `_scratch_mkfs >>$seqres.full 2>&1`
- Line 34: `export MOUNT_OPTIONS="-o fsync_mode=strict $MOUNT_OPTIONS"`
- Line 38: `_scratch_mount`
- Line 40: `mkdir $SCRATCH_MNT/a`
- Line 41: `$XFS_IO_PROG -f -c "pwrite -S 0xf1 0 16K" $SCRATCH_MNT/a/foo | _filter_xfs_io`
- Line 43: `_scratch_sync`
- Line 47: `mv $SCRATCH_MNT/a/foo $SCRATCH_MNT/a/bar`
- Line 48: `$XFS_IO_PROG -f -c "pwrite -S 0xba 0 16K" $SCRATCH_MNT/a/foo | _filter_xfs_io`
- Line 49: `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/a/foo`
- Line 52: `md5sum $SCRATCH_MNT/a/foo | _filter_scratch`
- Line 67: `_scratch_unmount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. dm-flakey is used to simulate a dropped write / power-fail boundary and then remount for recovery checks. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `metadata`, `log`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`, and uses capability gates such as `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Crash-recovery tests require dm-flakey behavior and metadata journaling; failures can appear as lost directory entries, stale content, or mount-time recovery errors.
- Thin-provisioning tests depend on device-mapper target behavior, pool exhaustion semantics, and correct cleanup of temporary block devices.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
