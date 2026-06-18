<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/072 -->
# sources/test-tools/xfstests/tests/overlay/072

## Purpose
Hardlink nlink regression test for upper hardlinks added behind a mounted overlay. It verifies overlay inode link counts do not underflow to zero when unaccounted hardlinks are later removed through the overlay.

## Important APIs, Types, And Functions
`_begin_fstest auto quick copyup hardlink` declares xfstests groups/tags: auto, quick, copyup, hardlink. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_fixed_by_kernel_commit`, `_require_scratch`.

## Control Flow
The test is a overlayfs regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 36: `_scratch_mkfs`; line 39: `mkdir -p $upperdir`; line 40: `touch $upperdir/0`; line 41: `ln $upperdir/0 $upperdir/1`; line 43: `_scratch_mount`; line 46: `stat -c '%h' $SCRATCH_MNT/0`; line 50: `ln $upperdir/0 $upperdir/2`; line 51: `ln $upperdir/0 $upperdir/3`; line 55: `rm $SCRATCH_MNT/2`; line 56: `rm $SCRATCH_MNT/3`.

## State And Persistence
State is kept in shell variables such as `upperdir`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/072 -->
