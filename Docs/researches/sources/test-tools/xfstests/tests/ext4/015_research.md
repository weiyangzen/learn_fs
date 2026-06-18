<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/015 -->
# sources/test-tools/xfstests/tests/ext4/015

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/015_research.md`.

Source read: 80 lines, SHA256 prefix `9137a12c18acb5bc`.

Purpose: FS QA Test No. 015 Create and populate an ext4 filesystem, corrupt an extent tree block, then see how the kernel and e2fsck deal with it. Override the default cleanup function..

Important APIs/types/functions: test tags `fuzzers punch prealloc`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`, `_require_scratch`, `_require_attrs`; helper functions `_cleanup()`; key variables `TESTDIR="${SCRATCH_MNT}/scratchdir"`, `TESTFILE="${TESTDIR}/testfile"`, `blksz="$(stat -f -c '%s' "${SCRATCH_MNT}")"`, `freeblks="$((3 * blksz / 12))"`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L27: _require_xfs_io_command "falloc"; L28: _require_xfs_io_command "fpunch"; L30: test -n "${FORCE_FUZZ}" || _require_scratch_ext4_crc; L37: _scratch_mkfs_ext4 > /dev/null 2>&1; L40: _scratch_mount; L45: $XFS_IO_PROG -f -c "falloc 0 $((blksz * freeblks))" "${SCRATCH_MNT}/bigfile" >> $seqres.full; L47: $XFS_IO_PROG -f -c "fpunch $((lblk * blksz)) ${blksz}" "${SCRATCH_MNT}/bigfile" >> $seqres.full; L52: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail"; L55: debugfs "${SCRATCH_DEV}" -R 'ex /bigfile' 2> /dev/null | grep '^ 0' | awk '{print $8}' | while read blk; do; L56: $XFS_IO_PROG -f -c "pwrite -S 0x62 $((blk * blksz + 8)) 8" "${SCRATCH_DEV}" >> $seqres.full; L60: _scratch_mount; L67: e2fsck -fy "${SCRATCH_DEV}" >> $seqres.full 2>&1; L70: _scratch_mount; L73: $XFS_IO_PROG -f -c "pwrite ${blksz} ${blksz}" "${SCRATCH_MNT}/bigfile" >> $seqres.full; L77: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly; uses fsck as the final persistence/integrity oracle.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on exact e2fsck/kernel reactions to damaged ext4 metadata.

Test signals: clean e2fsck verification; mount/statfs option visibility; visible subtest labels include + create scratch fs; + mount fs image; + make some files; + check fs; + corrupt image; + mount image.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/015 -->
