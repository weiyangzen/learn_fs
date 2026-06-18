<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/066 -->
# sources/test-tools/xfstests/tests/overlay/066

## Purpose
Sparse-file copy-up coverage. It creates empty, patterned-hole, and random-hole lower files of varied sizes, triggers copy-up by opening through overlay, and compares upper and lower trees while logging filefrag details on mismatch.

## Important APIs, Types, And Functions
`_begin_fstest auto quick copyup fiemap` declares xfstests groups/tags: auto, quick, copyup, fiemap. Imports `common/preamble`, `common/filter`. Local helpers: `do_cmd()`. Feature gates/fix annotations include `_require_test`, `_require_scratch`, `_require_fs_space`. External helper programs used include `$XFS_IO_PROG`, `$FILEFRAG_PROG`.

## Control Flow
The test is a overlayfs regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 23: `_scratch_mkfs`; line 131: `_scratch_mount`; line 142: `diff -qr ${upperdir} ${lowerdir} | tee -a $seqres.full`.

## State And Persistence
State is kept in shell variables such as `lowerdir`, `upperdir`, `testfile`, `file_size`, `min_iosize`, `max_iosize`, `iosize`, `max_pos`, `pos`, `min_hole`, `max_hole`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: space/quota tests are sensitive to scratch capacity, mkfs geometry, and background reclaim. Test signals: quiet success usually prints `Silence is golden`; content or output comparison is a primary failure signal.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/066 -->
