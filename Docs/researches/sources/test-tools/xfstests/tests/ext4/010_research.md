<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/010 -->
# sources/test-tools/xfstests/tests/ext4/010

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/010_research.md`.

Source read: 81 lines, SHA256 prefix `22e54a012dea45ad`.

Purpose: FS QA Test No. 010 Create and populate an ext4 filesystem, corrupt an inode bitmap, then see how the kernel and e2fsck deal with it. Override the default cleanup function..

Important APIs/types/functions: test tags `fuzzers`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_dumpe2fs`, `_require_attrs`, `_require_command "$RESIZE2FS_PROG" resize2fs`; helper functions `_cleanup()`; key variables `TESTDIR="${SCRATCH_MNT}/scratchdir"`, `TESTFILE="${TESTDIR}/testfile"`, `nr_groups="$($DUMPE2FS_PROG -g "${SCRATCH_DEV}" 2> /dev/null | tail -n 1 | cut -d : -f 1)"`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L28: _require_dumpe2fs; L29: test -n "${FORCE_FUZZ}" || _require_scratch_ext4_crc; L31: _require_command "$RESIZE2FS_PROG" resize2fs; L37: _scratch_mkfs_ext4 > /dev/null 2>&1; L38: $DUMPE2FS_PROG -g "${SCRATCH_DEV}" > /dev/null 2>&1 || _notrun "dumpe2fs -g not supported"; L39: $RESIZE2FS_PROG -M "${SCRATCH_DEV}" >> $seqres.full 2>&1; L40: nr_groups="$($DUMPE2FS_PROG -g "${SCRATCH_DEV}" 2> /dev/null | tail -n 1 | cut -d : -f 1)"; L43: _scratch_mount; L53: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail"; L56: $DUMPE2FS_PROG -g "${SCRATCH_DEV}" 2>/dev/null | awk -F ':' '{if (int($6) > 0) {print $6}}' | while read blk; do; L57: debugfs -w -n -R "zap_block ${blk}" "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "inode bitmap fuzz failed"; L61: _scratch_mount; L68: e2fsck -fy "${SCRATCH_DEV}" >> $seqres.full 2>&1; L71: _scratch_mount; L78: e2fsck -fn "${SCRATCH_DEV}" >> $seqres.full 2>&1 || _fail "fsck should not fail".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly; uses fsck as the final persistence/integrity oracle; resizes filesystem images or online filesystems.

Dependencies and integration points: Depends on xfstests common libraries, e2fsprogs debug/fsck utilities. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on exact e2fsck/kernel reactions to damaged ext4 metadata.

Test signals: clean e2fsck verification; visible subtest labels include + create scratch fs; + mount fs image; + make some files; + check fs; + corrupt image; + mount image.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/010 -->
