<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/035 -->
# sources/test-tools/xfstests/tests/ext4/035

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/035_research.md`.

Source read: 46 lines, SHA256 prefix `04b30048289a9420`.

Purpose: FSQA Test No. 035 Regression test for commit: f96c3ac8dfc2 ("ext4: fix crash during online resizing") This case tests a loss s_first_data_block on ext4 when computing maximum size with given number of group descriptor blocks. Filesystem with non-zero s_first_data_block can happen that computed maximum size lower than current size and leads to a BUG_ON in in ext4_alloc_group_tables() hitting on flex_gd->count == 0. Import common functions..

Important APIs/types/functions: test tags `auto quick resize`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_exclude_scratch_mount_option dax`, `_require_command "$RESIZE2FS_PROG" resize2fs`; key variables `encrypt="-O encrypt"`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L25: _exclude_scratch_mount_option dax; L26: _require_command "$RESIZE2FS_PROG" resize2fs; L36: _scratch_mount; L39: $RESIZE2FS_PROG $SCRATCH_DEV 262145 >> $seqres.full 2>&1; L42: $RESIZE2FS_PROG $SCRATCH_DEV 300000 >> $seqres.full 2>&1.

State and persistence behavior: mounts and unmounts test filesystems; resizes filesystem images or online filesystems.

Dependencies and integration points: Depends on xfstests common libraries, ext-family mkfs/tune utilities. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: visible subtest labels include Resizing to 262145 blocks; Resizing to 300000 blocks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/035 -->
