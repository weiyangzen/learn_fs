<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/058 -->
# sources/test-tools/xfstests/tests/overlay/058

## Purpose
Exercises overlayfs NFS-export decoding with warm and cold dentry caches, including disconnected non-directory dentries kept alive by background `open_by_handle` sleepers. It verifies upper and lower file handles before and after cache dropping.

## Important APIs, Types, And Functions
`_begin_fstest auto quick exportfs` declares xfstests groups/tags: auto, quick, exportfs. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`, `create_test_files()`, `test_file_handles()`. Feature gates/fix annotations include `_require_scratch`, `_require_test_program`, `_require_scratch_overlay_features`. External helper programs used include `open_by_handle`, `$here/src/open_by_handle`.

## Control Flow
The test is a overlayfs export/file-handle regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 29: `rm -f $tmp.*`; line 57: `mkdir -p $dir`; line 58: `$here/src/open_by_handle -cp $opt $dir $NUMFILES`; line 69: `$here/src/open_by_handle $* $dir $NUMFILES`; line 73: `_scratch_mkfs`; line 76: `_scratch_mount -o "index=on,nfs_export=on"`; line 91: `_scratch_cycle_mount "index=on,nfs_export=on"`.

## State And Persistence
State is kept in shell variables such as `lower`, `upper`, `work`, `NUMFILES`, `pids`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: file-handle behavior is sensitive to dcache warmth, inode identity, stale-handle semantics, and export feature availability. Test signals: volatile paths, ids, device names, or tool output are filtered before golden comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/058 -->
