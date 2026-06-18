<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/004 -->
# sources/test-tools/xfstests/tests/ext4/004

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/004_research.md`.

Source read: 65 lines, SHA256 prefix `08c7271b472efda6`.

Purpose: FSQA Test No. 004 Test "dump | restore"(as opposed to a tape) Override the default cleanup function..

Important APIs/types/functions: test tags `auto dump`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_test`, `_require_scratch`, `_require_command "$DUMP_PROG" dump`, `_require_command "$RESTORE_PROG" restore`; helper functions `_cleanup()`, `workout()`; key variables `dump_dir=$SCRATCH_MNT/dump_restore_dir`, `restore_dir=$TEST_DIR/dump_restore_dir`, `args=`_scale_fsstress_args -z -f creat=5 -f write=20 -f mkdir=5 -n 100 -p 15 -d $dump_dir``.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`, `workout()`. Representative operation sequence: L15: _kill_fsstress; L31: args=`_scale_fsstress_args -z -f creat=5 -f write=20 -f mkdir=5 -n 100 -p 15 -d $dump_dir`; L33: _run_fsstress $args; L38: $DUMP_PROG -0 -f - $dump_dir 2>/dev/null | $RESTORE_PROG -urvf - >> $seqres.full 2>&1; L52: _require_command "$DUMP_PROG" dump; L53: _require_command "$RESTORE_PROG" restore; L57: _scratch_mkfs_sized $((512 * 1024 * 1024)) >> $seqres.full 2>&1; L58: _scratch_mount; L62: diff -r $dump_dir $restore_dir.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: no unexpected stdout beyond the golden quiet marker; byte-for-byte compare of copied or restored data; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/004 -->
