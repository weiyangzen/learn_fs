<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/044 -->
# sources/test-tools/xfstests/tests/ext4/044

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/044_research.md`.

Source read: 72 lines, SHA256 prefix `5b283443dcfccf33`.

Purpose: FS QA Test No. 044 Test file timestamps are precise to nanoseconds with 256-byte inodes Import common functions..

Important APIs/types/functions: test tags `auto quick`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_test_program "t_get_file_time"`, `_require_metadata_journaling`; key variables `cur_time=`date '+%s %N'``, `sec=`echo $cur_time | $AWK_PROG {'print $1'}``, `nsec=`echo $cur_time | $AWK_PROG {'print $2'}``, `sec_atime=`$here/src/t_get_file_time $SCRATCH_MNT/tmp_file atime sec``, `sec_mtime=`$here/src/t_get_file_time $SCRATCH_MNT/tmp_file mtime sec``, `sec_ctime=`$here/src/t_get_file_time $SCRATCH_MNT/tmp_file ctime sec``, `nsec_atime=`$here/src/t_get_file_time $SCRATCH_MNT/tmp_file atime nsec``, `nsec_mtime=`$here/src/t_get_file_time $SCRATCH_MNT/tmp_file mtime nsec``, `nsec_ctime=`$here/src/t_get_file_time $SCRATCH_MNT/tmp_file ctime nsec``, `nsec_atime2=`$here/src/t_get_file_time $SCRATCH_MNT/tmp_file atime nsec``.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L23: _scratch_mkfs -t ext3 -I 256 >> $seqres.full 2>&1; L24: _scratch_mount; L55: _scratch_unmount >> $seqres.full 2>&1; L60: _mount -t ext3 `_scratch_mount_options $*` >> $seqres.full 2>&1 && _scratch_unmount >> $seqres.full 2>&1; L61: _scratch_mount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: contains timing-sensitive waits.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/044 -->
