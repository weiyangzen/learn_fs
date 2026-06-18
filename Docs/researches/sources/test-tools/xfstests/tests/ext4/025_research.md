<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/025 -->
# sources/test-tools/xfstests/tests/ext4/025

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/025_research.md`.

Source read: 35 lines, SHA256 prefix `0d1e497a91c27891`.

Purpose: FS QA Test ext4/025 Regression test for commit: 3a4b77c ("ext4: validate s_first_meta_bg at mount time"). get standard environment and checks.

Important APIs/types/functions: test tags `auto quick fuzzers dangerous`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch_nocheck`, `_require_command "$DEBUGFS_PROG" debugfs`, `_require_scratch_ext4_feature "bigalloc,meta_bg,^resize_inode"`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L19: _require_scratch_nocheck; L20: _require_command "$DEBUGFS_PROG" debugfs; L21: _require_scratch_ext4_feature "bigalloc,meta_bg,^resize_inode"; L24: _scratch_mkfs "-O bigalloc,meta_bg,^resize_inode" >> $seqres.full 2>&1; L28: $DEBUGFS_PROG -w -R "ssv first_meta_bg 842150400" $SCRATCH_DEV >> $seqres.full 2>&1; L31: _try_scratch_mount >> $seqres.full 2>&1 || echo "Fail to mount ext4 fs expectedly".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly.

Dependencies and integration points: Depends on xfstests common libraries, e2fsprogs debug/fsck utilities. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on exact e2fsck/kernel reactions to damaged ext4 metadata; bypasses normal scratch checking because corruption is intentional.

Test signals: visible subtest labels include Create ext4 fs and modify first_meta_bg's value; Try to mount a modified ext4 fs.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/025 -->
