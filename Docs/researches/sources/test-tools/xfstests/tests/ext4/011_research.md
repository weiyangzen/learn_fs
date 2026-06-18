<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/011 -->
# sources/test-tools/xfstests/tests/ext4/011

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/011_research.md`.

Source read: 65 lines, SHA256 prefix `f14db5c336495922`.

Purpose: FS QA Test No. 011 Create and populate an ext4 filesystem, corrupt the MMP block, then see how the kernel and e2fsck deal with it. Override the default cleanup function..

Important APIs/types/functions: test tags `fuzzers`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_attrs`; helper functions `_cleanup()`; key variables `TESTDIR="${SCRATCH_MNT}/scratchdir"`, `TESTFILE="${TESTDIR}/testfile"`, `blksz="$(stat -f -c '%s' "${SCRATCH_MNT}")"`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L28: test -n "${FORCE_FUZZ}" || _require_scratch_ext4_crc; L35: _scratch_mkfs_ext4 -O mmp -E mmp_update_interval=2 > /dev/null 2>&1; L38: _scratch_mount; L46: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail"; L49: blk="$(dumpe2fs "${SCRATCH_DEV}" 2> /dev/null | grep 'MMP block number' | sed -e 's/^MMP block number: *\([0-9]*\)$/\1/g')"; L50: $XFS_IO_PROG -f -c "pwrite -S 0x62 $((blk * blksz + 16)) 8" "${SCRATCH_DEV}" >> $seqres.full; L53: _try_scratch_mount 2> /dev/null && _fail "mount should fail due to bad MMP"; L56: e2fsck -fy "${SCRATCH_DEV}" >> $seqres.full 2>&1; L59: _try_scratch_mount || _fail "mount should not fail; MMP has been fixed"; L62: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; uses fsck as the final persistence/integrity oracle.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on exact e2fsck/kernel reactions to damaged ext4 metadata.

Test signals: clean e2fsck verification; mount/statfs option visibility; visible subtest labels include + create scratch fs; + mount fs image; + make some files; + check fs; + corrupt image; + mount image.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/011 -->
