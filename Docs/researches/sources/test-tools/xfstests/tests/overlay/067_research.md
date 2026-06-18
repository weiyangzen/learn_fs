<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/067 -->
# sources/test-tools/xfstests/tests/overlay/067

## Purpose
Non-samefs inode identity regression test. It ensures a middle-layer file on the same filesystem as upper does not export a real inode identity that causes `diff` to confuse the copied-up overlay file with the original lower file.

## Important APIs, Types, And Functions
`_begin_fstest auto quick copyup nonsamefs` declares xfstests groups/tags: auto, quick, copyup, nonsamefs. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_fixed_by_kernel_commit`, `_require_scratch_nocheck`, `_require_test`. External helper programs used include `$UMOUNT_PROG`.

## Control Flow
The test is a overlayfs regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 36: `rm -rf $lower`; line 37: `mkdir $lower`; line 39: `_scratch_mkfs >>$seqres.full 2>&1`; line 50: `_overlay_scratch_mount_dirs $middle:$lower $upper $work -o xino=off || \`; line 53: `stat $realfile >>$seqres.full`; line 54: `stat $testfile >>$seqres.full`; line 59: `stat $testfile >>$seqres.full`; line 62: `diff -q $realfile $testfile >>$seqres.full &&`; line 67: `stat $testfile >>$seqres.full`; line 70: `diff -q $realfile $testfile >>$seqres.full &&`.

## State And Persistence
State is kept in shell variables such as `lower`, `middle`, `upper`, `work`, `realfile`, `testfile`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: uses disruptive kernel/storage state such as cache dropping, shutdown, dm-error, error injection, or crash/hang triggers. Test signals: quiet success usually prints `Silence is golden`; content or output comparison is a primary failure signal; unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/067 -->
