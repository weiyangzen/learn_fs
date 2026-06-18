<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/005 -->
# sources/test-tools/xfstests/tests/ext4/005

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/005_research.md`.

Source read: 53 lines, SHA256 prefix `d2438bb20986971e`.

Purpose: FS QA Test 005 Test corruption issue in converting file with a hole at the beginning to non-extent based format These two commits fixed the corruption: ext4: be more strict when migrating to non-extent based file ext4: correctly migrate a file with a hole at the beginning Import common functions..

Important APIs/types/functions: test tags `auto quick metadata ioctl rw`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_command "$CHATTR_PROG" chattr`; key variables `testfile=$SCRATCH_MNT/$seq.attrtest`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L28: _scratch_mkfs >>$seqres.full 2>&1; L29: _scratch_mount; L40: $XFS_IO_PROG -fc "pwrite 4k 4k" -c "fsync" $testfile >>$seqres.full 2>&1; L49: $XFS_IO_PROG -c "pwrite 0 4k" $testfile >>$seqres.full 2>&1.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/005 -->
