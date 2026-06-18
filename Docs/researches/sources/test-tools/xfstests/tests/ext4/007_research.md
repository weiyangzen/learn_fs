<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/007 -->
# sources/test-tools/xfstests/tests/ext4/007

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/007_research.md`.

Source read: 99 lines, SHA256 prefix `58ed2ad9c6136691`.

Purpose: FS QA Test No. 007 Create and populate an ext4 filesystem, corrupt the primary superblock, then see how the kernel and e2fsck deal with it. Override the default cleanup function..

Important APIs/types/functions: test tags `fuzzers`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_attrs`; helper functions `_cleanup()`; key variables `TESTDIR="${SCRATCH_MNT}/scratchdir"`, `TESTFILE="${TESTDIR}/testfile"`, `blksz="$(stat -f -c '%s' "${SCRATCH_MNT}")"`, `nr_groups="$(dumpe2fs -g "${SCRATCH_DEV}" 2> /dev/null | tail -n 1 | cut -d : -f 1)"`, `inode="$(stat -c '%i' "${SCRATCH_MNT}/junk.${x}")"`, `broken=0`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L28: test -n "${FORCE_FUZZ}" || _require_scratch_ext4_crc; L35: _scratch_mkfs_ext4 > /dev/null 2>&1; L36: dumpe2fs -g "${SCRATCH_DEV}" > /dev/null 2>&1 || _notrun "dumpe2fs -g not supported"; L39: _scratch_mount; L41: nr_groups="$(dumpe2fs -g "${SCRATCH_DEV}" 2> /dev/null | tail -n 1 | cut -d : -f 1)"; L43: backup_sb="$(dumpe2fs -g "${SCRATCH_DEV}" 2> /dev/null | awk -F ':' 'BEGIN {x = 0;} {if (x == 0 && int($3) > 1) {print $3; x++;}}')"; L61: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail"; L64: dumpe2fs -g "${SCRATCH_DEV}" 2>/dev/null | awk -F ':' '{if ($1 == 0) {print $3}}' | while read blk; do; L65: debugfs -w -R "zap_block ${blk}" "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "primary sb fuzz failed"; L69: _try_scratch_mount 2> /dev/null && _fail "mount should not succeed"; L75: e2fsck -f -y -B "${blksz}" -b "${backup_sb}" "${SCRATCH_DEV}" >> $seqres.full 2>&1; L78: _scratch_mount; L96: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly; uses fsck as the final persistence/integrity oracle.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on exact e2fsck/kernel reactions to damaged ext4 metadata.

Test signals: clean e2fsck verification; mount/statfs option visibility; visible subtest labels include + create scratch fs; + mount fs image; + make some files; + check fs; + corrupt image; + mount image.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/007 -->
