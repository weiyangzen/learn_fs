# sources/test-tools/xfstests/tests/generic/335

## Purpose

Test that if we move one file between directories, fsync the parent directory of the old directory, power fail and remount the filesystem, the file is not lost and it's located at the destination directory Create our test directories and the file we will later check if it has disappeared. It is registered with `_begin_fstest auto quick metadata log` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `335` plus `_begin_fstest auto quick metadata log`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`. Capability gates: `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 78: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 61 `echo "Filesystem content before power failure:"`, line 72 `echo "Filesystem content after power failure:"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 19: `rm -f $tmp.*`
- Line 26: `_require_scratch`
- Line 27: `_require_dm_target flakey`
- Line 29: `_scratch_mkfs >>$seqres.full 2>&1`
- Line 32: `_scratch_mount`
- Line 36: `mkdir -p $SCRATCH_MNT/a/b`
- Line 37: `mkdir $SCRATCH_MNT/c`
- Line 38: `touch $SCRATCH_MNT/a/b/foo`
- Line 41: `_scratch_sync`
- Line 44: `mv $SCRATCH_MNT/a/b/foo $SCRATCH_MNT/c/`
- Line 49: `touch $SCRATCH_MNT/a/bar`
- Line 50: `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/a`
- Line 58: `$XFS_IO_PROG -c "fsync" $SCRATCH_MNT/c/foo`
- Line 76: `_scratch_unmount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. dm-flakey is used to simulate a dropped write / power-fail boundary and then remount for recovery checks. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `metadata`, `log`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`, and uses capability gates such as `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Crash-recovery tests require dm-flakey behavior and metadata journaling; failures can appear as lost directory entries, stale content, or mount-time recovery errors.
- Thin-provisioning tests depend on device-mapper target behavior, pool exhaustion semantics, and correct cleanup of temporary block devices.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
