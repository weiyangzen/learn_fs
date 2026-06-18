<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/086 -->
# sources/test-tools/xfstests/tests/overlay/086

## Purpose
Mount-option restriction test for `lowerdir+`/`datadir+`. It checks invalid combinations with legacy `lowerdir=`, invalid ordering of datadir before lowerdir, escaped-colon rejection for `lowerdir+`, successful unescaped colon handling, and displayed escaping for spaces.

## Important APIs, Types, And Functions
`_begin_fstest auto quick mount` declares xfstests groups/tags: auto, quick, mount. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_require_scratch_nocheck`, `_require_scratch_overlay_lowerdir_add_layers`. External helper programs used include `$MOUNT_PROG`, `$UMOUNT_PROG`.

## Control Flow
The test is a overlayfs data-only lower-layer behavior test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 22: `_scratch_mkfs`; line 31: `mkdir -p "$lowerdir_spaces" "$lowerdir_colons"`; line 36: `$MOUNT_PROG -t overlay none $SCRATCH_MNT \`; line 41: `$UMOUNT_PROG $SCRATCH_MNT 2>/dev/null`; line 43: `$MOUNT_PROG -t overlay none $SCRATCH_MNT \`; line 48: `$UMOUNT_PROG $SCRATCH_MNT 2>/dev/null`; line 50: `$MOUNT_PROG -t overlay none $SCRATCH_MNT \`; line 55: `$UMOUNT_PROG $SCRATCH_MNT 2>/dev/null`; line 58: `$MOUNT_PROG -t overlay none $SCRATCH_MNT \`; line 63: `$UMOUNT_PROG $SCRATCH_MNT 2>/dev/null`.

## State And Persistence
State is kept in shell variables such as `lowerdir_spaces`, `lowerdir_colons`, `lowerdir_colons_esc`, `lowerdir`, `upperdir`, `workdir`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: xattr and overlay metadata assertions depend on trusted/user xattr support and exact kernel on-disk semantics. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/086 -->
