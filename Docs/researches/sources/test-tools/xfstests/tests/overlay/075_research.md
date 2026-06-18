<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/075 -->
# sources/test-tools/xfstests/tests/overlay/075

## Purpose
Runs `t_immutable` against immutable and append-only files prepared in the lower layer. It observes behavior before copy-up, triggers directory/file copy-up, cycles the mount, and verifies flags lost during copy-up do not leave undeletable overlay state.

## Important APIs, Types, And Functions
`_begin_fstest auto quick perms` declares xfstests groups/tags: auto, quick, perms. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`. Feature gates/fix annotations include `_require_chattr`, `_require_test_program`, `_require_scratch`. External helper programs used include `t_immutable`, `$here/src/t_immutable`.

## Control Flow
The test is a overlayfs regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 30: `rm -f $tmp.*`; line 41: `_scratch_mkfs`; line 44: `mkdir -p $lowerdir`; line 45: `mkdir -p $upperdir`; line 56: `mkdir $dir/subdir`; line 61: `_scratch_mount`; line 72: `touch $dir/subdir`; line 80: `touch $file > /dev/null 2>&1`; line 85: `_scratch_cycle_mount`; line 89: `rm -rf $SCRATCH_MNT/testdir.before`.

## State And Persistence
State is kept in shell variables such as `timmutable`, `lowerdir`, `upperdir`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/075 -->
