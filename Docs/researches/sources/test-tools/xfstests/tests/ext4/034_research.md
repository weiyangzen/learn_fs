<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/034 -->
# sources/test-tools/xfstests/tests/ext4/034

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/034_research.md`.

Source read: 63 lines, SHA256 prefix `ea6edeb791a61d44`.

Purpose: FS QA Test 034 Regression test for a ENOSPC warning when both quota and "-o dioread_nolock,nodelalloc" is used. The bug was fixed by commit "ext4: make sure enough credits are reserved for dioread_nolock writes" Import common functions. Modify as appropriate..

Important APIs/types/functions: test tags `auto quick quota fiemap prealloc`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_quota`, `_require_nobody`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fiemap"`, `_require_xfs_io_command "syncfs"`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L14: _begin_fstest auto quick quota fiemap prealloc; L27: _require_xfs_io_command "falloc"; L28: _require_xfs_io_command "fiemap"; L32: _scratch_mkfs "-O quota" > $seqres.full 2>&1; L33: _scratch_mount "-o dioread_nolock,nodelalloc" > $seqres.full 2>&1; L44: $XFS_IO_PROG -f -c "pwrite 0 4k" -c "falloc 4k 4k" -c "pwrite 8k 4k" \; L48: $XFS_IO_PROG -c "fiemap -v" $SCRATCH_MNT/foobar >> $seqres.full; L51: $XFS_IO_PROG -c "pwrite 4k 4k" $SCRATCH_MNT/foobar >> $seqres.full; L54: $XFS_IO_PROG -f -c "pwrite 0 4k" -c "fsync" $SCRATCH_MNT/dummy >> $seqres.full; L59: $XFS_IO_PROG -c "syncfs" $SCRATCH_MNT >> $seqres.full.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; changes quota/qgroup accounting state.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands, quota userspace tools. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: quota accounting regressions can be silent until unmount or rescan.

Test signals: fiemap extent layout and flags; visible subtest labels include Format and mount; Create the original file; Set hard quota; Create 2 level extent tree (btree) for foobar with a unwritten extent; Convert unwritten extent to written and collapse extent tree to inode; Create a new file and do fsync to force a jbd2 commit.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/034 -->
