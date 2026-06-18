<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/024 -->
# sources/test-tools/xfstests/tests/ext4/024

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/024_research.md`.

Source read: 53 lines, SHA256 prefix `5e45cbcfd70b7ac9`.

Purpose: FS QA Test ext4/024 Regression test for 0d06863f903a ("ext4: don't BUG when truncating encrypted inodes on the orphan list"). get standard environment and checks.

Important APIs/types/functions: test tags `auto quick encrypt dangerous`; common harness imports `. ./common/preamble`, `. ./common/encrypt`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch_encryption`, `_require_command "$KEYCTL_PROG" keyctl`; key variables `keydesc=$(_generate_session_encryption_key)`, `inum=$(stat -c '%i' $SCRATCH_MNT/edir/file)`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L19: _require_scratch_encryption; L37: _scratch_mkfs_encrypted &>>$seqres.full; L38: _scratch_mount; L44: _scratch_unmount; L45: debugfs -w -R "set_super_value s_last_orphan $inum" $SCRATCH_DEV &>>$seqres.full; L48: _try_scratch_mount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: visible subtest labels include Didn't crash!.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/024 -->
