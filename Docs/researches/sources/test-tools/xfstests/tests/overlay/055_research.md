<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/055 -->
# sources/test-tools/xfstests/tests/overlay/055

## Purpose
Variant of overlay/054 for a lower redirected merge directory in a multi-lower, non-samefs setup. It verifies that file handles for lower directories below a lower-layer redirect are encoded with the right copy-up/index behavior and remain decodable after the redirected ancestor is renamed.

## Important APIs, Types, And Functions
`_begin_fstest auto quick copyup redirect exportfs nonsamefs` declares xfstests groups/tags: auto, quick, copyup, redirect, exportfs, nonsamefs. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`, `create_test_files()`, `test_file_handles()`, `create_dirs()`, `mount_dirs()`, `unmount_dirs()`. Feature gates/fix annotations include `_fixed_by_kernel_commit`, `_require_test`, `_require_test_program`, `_require_scratch_nocheck`, `_require_scratch_overlay_features`. External helper programs used include `$UMOUNT_PROG`, `open_by_handle`, `$here/src/open_by_handle`.

## Control Flow
The test is a overlayfs export/file-handle regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 36: `rm -f $tmp.*`; line 40: `$UMOUNT_PROG $SCRATCH_MNT 2>/dev/null`; line 74: `mkdir -p $dir`; line 75: `$here/src/open_by_handle -cp $opt $dir $NUMFILES`; line 86: `$here/src/open_by_handle $* $dir $NUMFILES`; line 93: `rm -rf $lower`; line 94: `mkdir $lower`; line 97: `_scratch_mkfs`; line 104: `_overlay_scratch_mount_dirs $middle:$lower $upper $work \`; line 112: `$UMOUNT_PROG $SCRATCH_MNT`.

## State And Persistence
State is kept in shell variables such as `lower`, `middle`, `upper`, `work`, `NUMFILES`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: file-handle behavior is sensitive to dcache warmth, inode identity, stale-handle semantics, and export feature availability; xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/055 -->
