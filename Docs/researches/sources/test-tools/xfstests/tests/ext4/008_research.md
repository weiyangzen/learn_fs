<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/008 -->
# sources/test-tools/xfstests/tests/ext4/008

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/008_research.md`.

Source read: 80 lines, SHA256 prefix `ba4f76838f1a7667`.

Purpose: FS QA Test No. 008 Create and populate an ext4 filesystem, corrupt a group descriptor, then see how the kernel and e2fsck deal with it. Override the default cleanup function..

Important APIs/types/functions: test tags `fuzzers`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_attrs`; helper functions `_cleanup()`; key variables `TESTDIR="${SCRATCH_MNT}/scratchdir"`, `TESTFILE="${TESTDIR}/testfile"`, `inode="$(stat -c '%i' "${SCRATCH_MNT}/junk.${x}")"`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L28: test -n "${FORCE_FUZZ}" || _require_scratch_ext4_crc; L35: _scratch_mkfs_ext4 > /dev/null 2>&1; L36: dumpe2fs -g "${SCRATCH_DEV}" > /dev/null 2>&1 || _notrun "dumpe2fs -g not supported"; L39: _scratch_mount; L57: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail"; L60: dumpe2fs -g "${SCRATCH_DEV}" 2>/dev/null | awk -F ':' '{if (int($4) != -1) {print $4}}' | sed -e 's/-.*$//g' | awk '{if (int($1) > 0) {print $1}}' | while read blk; do; L61: debugfs -w -R "zap_block ${blk}" "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "group descriptor fuzz failed"; L65: _try_scratch_mount 2> /dev/null && _fail "mount should not succeed"; L68: e2fsck -fy "${SCRATCH_DEV}" >> $seqres.full 2>&1; L69: e2fsck -fy "${SCRATCH_DEV}" >> $seqres.full 2>&1; L72: _scratch_mount; L77: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly; uses fsck as the final persistence/integrity oracle.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on exact e2fsck/kernel reactions to damaged ext4 metadata.

Test signals: clean e2fsck verification; visible subtest labels include + create scratch fs; + mount fs image; + make some files; + check fs; + corrupt image; + mount image.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/008 -->
