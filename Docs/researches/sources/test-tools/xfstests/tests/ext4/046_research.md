<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/046 -->
# sources/test-tools/xfstests/tests/ext4/046

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/046_research.md`.

Source read: 78 lines, SHA256 prefix `58ab61897c8da679`.

Purpose: FS QA Test No. ext4/046 Test writes to falloc file with filesize > 4GB and make sure to verify the file checksum both before and after mount. This test is to check whether unwritten extents gets properly converted to written extent on a filesystem with bs < ps with dioread_nolock. Import common functions..

Important APIs/types/functions: test tags `auto prealloc quick`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_require_check_dmesg`, `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_xfs_io_command "falloc"`, `_require_scratch_size $((6 * 1024 * 1024)) #kB`; key variables `err_str="can't mount with dioread_nolock if block size != PAGE_SIZE"`, `blksz=$(_get_file_block_size $SCRATCH_MNT)`, `testfile=$SCRATCH_MNT/testfile-$seq`, `fsize=$((5 * 1024 * 1024 * 1024))`, `off=$((3 * 1024 * 1024 * 1024))`, `off=$(($off + (2*$blksz)))`, `off=$((4 * 1024 * 1024 * 1024))`, `off=$(($off + (2*$blksz)))`, `md5_pre=`md5sum $testfile | cut -d' ' -f1``, `md5_post=`md5sum $testfile | cut -d' ' -f1``.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L18: _require_check_dmesg; L22: _require_xfs_io_command "falloc"; L23: _require_scratch_size $((6 * 1024 * 1024)) #kB; L25: _scratch_mkfs >> $seqres.full 2>&1; L26: if ! _try_scratch_mount "-o dioread_nolock" >> $seqres.full 2>&1; then; L28: _check_dmesg_for ${err_str}; L43: $XFS_IO_PROG -f -c "falloc 0 $fsize" $testfile >> $seqres.full 2>&1; L48: $XFS_IO_PROG -f \; L58: $XFS_IO_PROG -f \; L65: md5_pre=`md5sum $testfile | cut -d' ' -f1`; L68: _scratch_cycle_mount; L71: md5_post=`md5sum $testfile | cut -d' ' -f1`; L73: test $md5_pre != $md5_post && echo "md5sum mismatch".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: no unexpected stdout beyond the golden quiet marker; matching file digests before and after remount/send/receive; absence or presence of expected dmesg warnings; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/046 -->
