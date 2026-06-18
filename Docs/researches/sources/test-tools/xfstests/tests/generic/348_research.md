# sources/test-tools/xfstests/tests/generic/348

## Purpose

Test creating a symlink, fsync its parent directory, power fail and mount again the filesystem. After these steps the symlink should exist and its content must match what we specified when we created it (must not be empty or point to something else). It is registered with `_begin_fstest auto quick metadata` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `348` plus `_begin_fstest auto quick metadata`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`. Capability gates: `_require_scratch`, `_require_symlinks`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 58: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 53 `echo "Symlink contents after log replay:"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 20: `rm -f $tmp.*`
- Line 27: `_require_scratch`
- Line 29: `_require_dm_target flakey`
- Line 31: `_scratch_mkfs >>$seqres.full 2>&1`
- Line 34: `_scratch_mount`
- Line 36: `mkdir $SCRATCH_MNT/testdir1`
- Line 38: `_scratch_sync`
- Line 43: `ln -s $SCRATCH_MNT/foo1 $SCRATCH_MNT/testdir1/bar1`
- Line 44: `$XFS_IO_PROG -c fsync $SCRATCH_MNT/testdir1`
- Line 45: `mkdir $SCRATCH_MNT/testdir2`
- Line 46: `ln -s $SCRATCH_MNT/foo2 $SCRATCH_MNT/testdir2/bar2`
- Line 47: `$XFS_IO_PROG -c fsync $SCRATCH_MNT/testdir2`
- Line 51: `_flakey_drop_and_remount`
- Line 57: `_scratch_unmount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. dm-flakey is used to simulate a dropped write / power-fail boundary and then remount for recovery checks. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `metadata`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`, and uses capability gates such as `_require_scratch`, `_require_symlinks`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Crash-recovery tests require dm-flakey behavior and metadata journaling; failures can appear as lost directory entries, stale content, or mount-time recovery errors.
- Thin-provisioning tests depend on device-mapper target behavior, pool exhaustion semantics, and correct cleanup of temporary block devices.
- Symlink persistence tests are metadata-focused and can fail through lost directory updates, wrong target payloads, or fast/slow symlink representation differences.

## Test Signals

The pass signal is symlink target reads. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
