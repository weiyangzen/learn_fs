<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/045 -->
# sources/test-tools/xfstests/tests/ext4/045

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/045_research.md`.

Source read: 95 lines, SHA256 prefix `7a00ee40792aba1c`.

Purpose: FS QA Test No. 045 Test subdirectory limit of ext4. We create more than 65000 subdirectories on the ext4 filesystem..

Important APIs/types/functions: test tags `auto dir`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_scratch_ext4_feature large_dir`, `_require_test_program "t_create_short_dirs"`, `_require_test_program "t_create_long_dirs"`, `_require_dumpe2fs`; helper functions `workout()`; key variables `SHORT_DIR=1`, `LONG_DIR=2`, `dir_name_len="short name"`, `dir_name_len="long name"`, `nr_dirs=`ls $3 | wc -l``, `DIR_NUM=65537`, `DIR_LEN=( $SHORT_DIR $LONG_DIR )`, `PARENT_DIR="$SCRATCH_MNT/subdir"`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `workout()`. Representative operation sequence: L23: _require_scratch_ext4_feature large_dir; L26: _require_dumpe2fs; L46: _scratch_mkfs "-O extent,dir_nlink,dir_index,large_dir -I 256" >> $seqres.full 2>&1; L47: _scratch_mount; L61: _scratch_unmount; L71: _scratch_unmount; L75: _scratch_unmount; L78: $DUMPE2FS_PROG -h $SCRATCH_DEV 2>> $seqres.full | grep '^Filesystem features' | grep -q dir_nlink.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, e2fsprogs debug/fsck utilities. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/045 -->
