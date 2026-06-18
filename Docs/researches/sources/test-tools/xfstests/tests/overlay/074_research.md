<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/074 -->
# sources/test-tools/xfstests/tests/overlay/074

## Purpose
Dangerous malformed file-handle regression test. It verifies handle-size query support, validates a normal exported handle, then crafts malformed v0/v1 overlay file handles and expects open-by-handle failure instead of kernel crash or bounds warning.

## Important APIs, Types, And Functions
`_begin_fstest auto quick exportfs dangerous` declares xfstests groups/tags: auto, quick, exportfs, dangerous. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_fixed_by_kernel_commit`, `_require_scratch`, `_require_test_program`, `_require_scratch_overlay_features`. External helper programs used include `open_by_handle`, `$here/src/open_by_handle`, `$XFS_IO_PROG`.

## Control Flow
The test is a overlayfs export/file-handle regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 34: `_scratch_mkfs`; line 35: `_scratch_mount -o "index=on,nfs_export=on"`; line 40: `$here/src/open_by_handle -cp $testdir`; line 43: `$here/src/open_by_handle -pz $testdir`; line 46: `$here/src/open_by_handle -o $tmp.file_handle $testdir`; line 49: `$here/src/open_by_handle -i $tmp.file_handle $testdir`; line 58: `cp $tmp.file_handle $tmp.file_handle_v0`; line 59: `$XFS_IO_PROG -c "pwrite -S 0 0 8" -c "pwrite -S 1 0 1" -c "pwrite -S 0xfb 4 1" \`; line 65: `cp $tmp.file_handle $tmp.file_handle_v1`; line 66: `$XFS_IO_PROG -c "pwrite -S 0 0 8" -c "pwrite -S 1 0 1" -c "pwrite -S 0xf8 4 1" \`.

## State And Persistence
State is kept in shell variables such as `testdir`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: marked dangerous, so it can crash, hang, or exercise kernel failure paths; file-handle behavior is sensitive to dcache warmth, inode identity, stale-handle semantics, and export feature availability. Test signals: quiet success usually prints `Silence is golden`; content or output comparison is a primary failure signal; explicit `_fail` calls mark invariant violations.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/074 -->
