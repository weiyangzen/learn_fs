<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/043 -->
# sources/test-tools/xfstests/tests/ext4/043

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/043_research.md`.

Source read: 38 lines, SHA256 prefix `958ee187e7f81945`.

Purpose: FS QA Test No. 043 Test file timestamps are only precise to seconds with 128-byte inodes." Import common functions..

Important APIs/types/functions: test tags `auto quick`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_require_scratch`, `_require_test_program "t_get_file_time"`; key variables `atime=`$here/src/t_get_file_time $SCRATCH_MNT/tmp_file atime nsec``, `mtime=`$here/src/t_get_file_time $SCRATCH_MNT/tmp_file mtime nsec``, `ctime=`$here/src/t_get_file_time $SCRATCH_MNT/tmp_file ctime nsec``.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L23: _scratch_mkfs -I 128 >> $seqres.full 2>&1; L24: _scratch_mount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden; nsec should be zero when extended timestamps are disabled.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/043 -->
