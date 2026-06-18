<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/073 -->
# sources/test-tools/xfstests/tests/overlay/073

## Purpose
Whiteout inode sharing test. It deletes lower files/dirs through overlay, expects shared whiteout hardlinks in upper/index, and validates a single temporary whiteout object rather than one inode per whiteout.

## Important APIs, Types, And Functions
`_begin_fstest auto quick whiteout` declares xfstests groups/tags: auto, quick, whiteout. Imports `common/preamble`, `common/filter`. Local helpers: `make_lower_files()`, `make_whiteout_files()`, `check_whiteout_files()`, `run_test_case()`. Feature gates/fix annotations include `_require_scratch`, `_require_scratch_overlay_features`.

## Control Flow
The test is a overlayfs export/file-handle regression test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 38: `mkdir $lowerdir/dir`; line 40: `touch $lowerdir/${name} &>/dev/null`; line 53: `rm $SCRATCH_MNT/* &>/dev/null`; line 81: `_scratch_mkfs`; line 85: `_scratch_mount -o "index=on,nfs_export=off"`; line 88: `_scratch_unmount`.

## State And Persistence
State is kept in shell variables such as `lowerdir`, `upperdir`, `workdir`, `file_count`, `link_count`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: file-handle behavior is sensitive to dcache warmth, inode identity, stale-handle semantics, and export feature availability; xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: quiet success usually prints `Silence is golden`; unsupported environments are skipped with `_notrun`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/073 -->
