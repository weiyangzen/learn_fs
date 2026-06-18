<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/081 -->
# sources/test-tools/xfstests/tests/overlay/081

## Purpose
Persistent and unique overlay fsid test for `uuid=null`, `uuid=auto`, and `uuid=on`. It compares `stat -f` fsids against base fsids for existing impure overlays, explicit opt-in/out, read-only non-upper overlays, and freshly created overlays.

## Important APIs, Types, And Functions
`_begin_fstest auto quick` declares xfstests groups/tags: auto, quick. Imports `common/preamble`, `common/filter`, `common/attr`. External helper programs used include `$UMOUNT_PROG`.

## Control Flow
The test is a overlayfs regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 18: `_scratch_mkfs >>$seqres.full 2>&1`; line 24: `mkdir -p $upperdir/test_dir`; line 25: `mkdir -p $lowerdir/test_dir`; line 39: `_overlay_scratch_mount_dirs $lowerdir $upperdir $workdir -o uuid=null 2>/dev/null || \`; line 49: `$UMOUNT_PROG $SCRATCH_MNT`; line 52: `_scratch_mount`; line 58: `$UMOUNT_PROG $SCRATCH_MNT`; line 61: `_scratch_mount -o uuid=on`; line 68: `$UMOUNT_PROG $SCRATCH_MNT`; line 71: `_scratch_mount`.

## State And Persistence
State is kept in shell variables such as `upperdir`, `workdir`, `lowerdir`, `test_dir`, `upper_fsid`, `lower_fsid`, `ovl_fsid`, `ovl_unique_fsid`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`; content or output comparison is a primary failure signal; unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/081 -->
