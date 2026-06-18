<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/054 -->
# sources/test-tools/xfstests/tests/ext4/054

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/054_research.md`.

Source read: 85 lines, SHA256 prefix `98c983a19ec7c248`.

Purpose: FS QA Test 054 Regression test for kernel commit: 1. 0f2f87d51aebc (ext4: prevent partial update of the extent blocks) 2. 9c6e071913792 (ext4: check for inconsistent extents between index \ and leaf block) 3. 8dd27fecede55 (ext4: check for out-of-order index extents in \ ext4_valid_extent_entries()) Import common functions.

Important APIs/types/functions: test tags `auto quick dangerous_fuzzers prealloc punch`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch_nocheck`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "pwrite"`, `_require_xfs_io_command "fsync"`, `_require_xfs_io_command "fpunch"`, `_require_command "$DEBUGFS_PROG" debugfs`; key variables `TEST_FILE="${SCRATCH_MNT}/testfile"`, `offset=$((1024 * 128 * i))`, `offset=$((offset + 1024 * 64))`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L23: _require_scratch_nocheck; L24: _require_xfs_io_command "falloc"; L27: _require_xfs_io_command "fpunch"; L28: _require_command "$DEBUGFS_PROG" debugfs; L32: _scratch_mkfs_blocksized 1024 >> $seqres.full 2>&1; L33: _scratch_mount; L49: $XFS_IO_PROG -c "falloc $offset $((1024 * 64))" $TEST_FILE >> $seqres.full; L51: $XFS_IO_PROG -c "pwrite $offset $((1024 * 64))" $TEST_FILE >> $seqres.full; L52: $XFS_IO_PROG -c "fsync" $TEST_FILE >> $seqres.full; L55: $XFS_IO_PROG -c "fpunch $((1024 * 5376)) $((1024 * 256))" $TEST_FILE \; L57: $XFS_IO_PROG -c "fsync" $TEST_FILE >> $seqres.full; L58: $XFS_IO_PROG -c "falloc $((1024 * 5376)) $((1024 * 64))" $TEST_FILE \; L60: $XFS_IO_PROG -c "fsync" $TEST_FILE >> $seqres.full; L62: _scratch_unmount >> $seqres.full 2>&1; L64: $DEBUGFS_PROG -w -R "set_inode_field testfile block[6] 0x1600" $SCRATCH_DEV \; L75: _scratch_mount "-o nodelalloc"; L76: $XFS_IO_PROG -c "pwrite $((1024 * 5568)) $((1024 * 64))" $TEST_FILE \.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands, e2fsprogs debug/fsck utilities. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: deliberately corrupts metadata and can trigger kernel failure paths; bypasses normal scratch checking because corruption is intentional.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/054 -->
