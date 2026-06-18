<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/009 -->
# sources/test-tools/xfstests/tests/ext4/009

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/009_research.md`.

Source read: 90 lines, SHA256 prefix `1bf5fc3e97887ff5`.

Purpose: FS QA Test No. 009 Create and populate an ext4 filesystem, corrupt a block bitmap, then see how the kernel and e2fsck deal with it. Override the default cleanup function..

Important APIs/types/functions: test tags `fuzzers prealloc`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_xfs_io_command "falloc"`, `_require_scratch`, `_require_attrs`; helper functions `_cleanup()`; key variables `TESTDIR="${SCRATCH_MNT}/scratchdir"`, `TESTFILE="${TESTDIR}/testfile"`, `nr_groups="$(dumpe2fs -g "${SCRATCH_DEV}" 2> /dev/null | tail -n 1 | cut -d : -f 1)"`, `blksz="$(stat -f -c '%s' "${SCRATCH_MNT}")"`, `freeblks="$(stat -f -c '%a' "${SCRATCH_MNT}")"`, `b_bytes="$(stat -c '%B' "${SCRATCH_MNT}/bigfile")"`, `after="$(stat -c '%b' "${SCRATCH_MNT}/bigfile")"`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L27: _require_xfs_io_command "falloc"; L29: test -n "${FORCE_FUZZ}" || _require_scratch_ext4_crc; L36: _scratch_mkfs_ext4 > /dev/null 2>&1; L37: dumpe2fs -g "${SCRATCH_DEV}" > /dev/null 2>&1 || _notrun "dumpe2fs -g not supported"; L38: nr_groups="$(dumpe2fs -g "${SCRATCH_DEV}" 2> /dev/null | tail -n 1 | cut -d : -f 1)"; L41: _scratch_mount; L48: $XFS_IO_PROG -f -c "falloc 0 $((blksz * freeblks))" "${SCRATCH_MNT}/bigfile2" >> $seqres.full; L52: _scratch_mount; L58: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail"; L61: dumpe2fs -g "${SCRATCH_DEV}" 2>/dev/null | awk -F ':' '{if (int($5) > 0) {print $5}}' | while read blk; do; L62: debugfs -w -n -R "zap_block -p 0xff ${blk}" "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "block bitmap fuzz failed"; L66: _scratch_mount; L70: $XFS_IO_PROG -f -c "falloc 0 $((blksz * freeblks))" "${SCRATCH_MNT}/bigfile" >> $seqres.full 2> /dev/null; L73: test "$((after * b_bytes))" -lt "$((blksz * freeblks / 4))" || _fail "falloc should fail"; L77: e2fsck -fy "${SCRATCH_DEV}" >> $seqres.full 2>&1; L80: _scratch_mount; L83: $XFS_IO_PROG -f -c "falloc 0 $((blksz * freeblks))" "${SCRATCH_MNT}/bigfile" >> $seqres.full; L87: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly; uses fsck as the final persistence/integrity oracle.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on exact e2fsck/kernel reactions to damaged ext4 metadata.

Test signals: clean e2fsck verification; mount/statfs option visibility; visible subtest labels include + create scratch fs; + mount fs image; + make some files; + check fs; + corrupt image; + mount image.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/009 -->
