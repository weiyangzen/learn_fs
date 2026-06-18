<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/020 -->
# sources/test-tools/xfstests/tests/ext4/020

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/020_research.md`.

Source read: 56 lines, SHA256 prefix `984bc16f71969320`.

Purpose: FS QA Test 020 Test partial blocksize defrag integrity issue. Calling EXT4_IOC_MOVE_EXTENT on file not aligned with block size and block size is smaller than page size would cause integrity issue on the partial-blocksize part when copying data between orign file and donor file. Import common functions..

Important APIs/types/functions: test tags `auto quick ioctl rw defrag`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/defrag`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_defrag`, `_require_test_program "e4compact"`; key variables `e4compact=$here/src/e4compact`, `testfile=$SCRATCH_MNT/$seq.orig`, `donorfile=$SCRATCH_MNT/$seq.donor`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L31: _scratch_mkfs >>$seqres.full 2>&1; L32: _scratch_mount; L36: $XFS_IO_PROG -fc "pwrite -S 0xaa 0 1m" -c "fsync" $donorfile | _filter_xfs_io; L40: $XFS_IO_PROG -fc "pwrite -S 0xbb 0 1023" -c "fsync" $testfile | _filter_xfs_io; L43: md5sum $testfile > $tmp.md5sum; L52: md5sum -c $tmp.md5sum | _filter_scratch.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; drops page cache to force media-backed reads.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: requires privileged cache dropping and can perturb the host.

Test signals: matching file digests before and after remount/send/receive; visible subtest labels include 3 > /proc/sys/vm/drop_caches.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/020 -->
