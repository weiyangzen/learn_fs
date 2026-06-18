<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/013 -->
# sources/test-tools/xfstests/tests/ext4/013

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/013_research.md`.

Source read: 103 lines, SHA256 prefix `ac7300fe9852d908`.

Purpose: FS QA Test No. 013 Create and populate an ext4 filesystem, corrupt an inode, then see how the kernel and e2fsck deal with it. Override the default cleanup function..

Important APIs/types/functions: test tags `fuzzers`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_attrs`; helper functions `_cleanup()`; key variables `TESTDIR="${SCRATCH_MNT}/scratchdir"`, `TESTFILE="${TESTDIR}/testfile"`, `inode="$(stat -c '%i' "${SCRATCH_MNT}/junk.${x}")"`, `inode="$(stat -c '%i' "${TESTFILE}.1")"`, `broken=0`, `broken=0`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L28: test -n "${FORCE_FUZZ}" || _require_scratch_ext4_crc; L35: _scratch_mkfs_ext4 > /dev/null 2>&1; L38: _scratch_mount; L57: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail"; L60: blk="$(debugfs -R "imap <$inode>" "${SCRATCH_DEV}" 2> /dev/null | grep located | sed -e 's/^.*block \([0-9]*\),.*$/\1/g')"; L61: debugfs -w -R "zap_block ${blk}" "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "inode fuzz failed"; L64: _scratch_mount; L79: e2fsck -fy "${SCRATCH_DEV}" >> $seqres.full 2>&1; L82: _scratch_mount; L100: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly; uses fsck as the final persistence/integrity oracle.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on exact e2fsck/kernel reactions to damaged ext4 metadata.

Test signals: clean e2fsck verification; visible subtest labels include + create scratch fs; + mount fs image; + make some files; + check fs; + corrupt image; + mount image.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/013 -->
