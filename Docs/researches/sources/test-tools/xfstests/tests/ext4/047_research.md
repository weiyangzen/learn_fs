<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/047 -->
# sources/test-tools/xfstests/tests/ext4/047

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/047_research.md`.

Source read: 41 lines, SHA256 prefix `77b44652b02b384b`.

Purpose: FS QA Test 047 This is a regression test for kernel patch: commit aa2f77920b74 ("ext4: disallow modifying DAX inode flag if inline_data has been set") Import common functions..

Important APIs/types/functions: test tags `auto quick dax`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch_dax_mountopt "dax=always"`, `_require_dax_iflag`, `_require_scratch_ext4_feature "inline_data"`; key variables `TESTFILE=$SCRATCH_MNT/testfile`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L19: _require_scratch_dax_mountopt "dax=always"; L21: _require_scratch_ext4_feature "inline_data"; L25: _scratch_mkfs_ext4 -O inline_data > $seqres.full 2>&1; L27: _scratch_mount "-o dax=inode" >> $seqres.full 2>&1; L33: if $XFS_IO_PROG -c "chattr +x" $TESTFILE >> $seqres.full 2>&1; then; L34: _scratch_cycle_mount "dax=inode".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/047 -->
