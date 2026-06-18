<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/058 -->
# sources/test-tools/xfstests/tests/ext4/058

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/058_research.md`.

Source read: 33 lines, SHA256 prefix `94aa14b7eaf22662`.

Purpose: FS QA Test 058 Set 256 blocks in a block group, then inject I/O pressure, it will trigger off kernel BUG in ext4_mb_mark_diskspace_used Regression test for commit a08f789d2ab5 ext4: fix bug_on ext4_mb_use_inode_pa.

Important APIs/types/functions: test tags `auto quick`; common harness imports `. ./common/preamble`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_fixed_by_kernel_commit a08f789d2ab5 \`, `_require_scratch`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L24: _scratch_mkfs -g 256 >> $seqres.full 2>&1 || _fail "mkfs failed"; L25: _scratch_mount; L27: _run_fsstress -d $SCRATCH_MNT/stress -n 1000.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/058 -->
