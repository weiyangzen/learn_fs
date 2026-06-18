<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ceph/002 -->
# sources/test-tools/xfstests/tests/ceph/002

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ceph/002_research.md`.

Source read: 64 lines, SHA256 prefix `525809cd9a60fcc5`.

Purpose: FS QA Test No. ceph/002 Test bug found while testing copy_file_range. This bug was an issue with how the OSDs handled the truncate_seq, copying it from the original object into the destination object. This test ensures the kernel client correctly handles fixed/non-fixed OSDs. The bug was tracked here: https://tracker.ceph.com/issues/37378 The most relevant commits are: ceph OSD: dcd6a99ef9f5 ("osd: add new 'copy-from2' operation") linux kernel: 78beb0ff2fec ("ceph: use copy-from2 op in copy_file_range") get standard environment.

Important APIs/types/functions: test tags `auto quick copy_range`; common harness imports `. ./common/preamble`, `. common/filter`, `. common/attr`; requirements/fixed gates `_require_xfs_io_command "copy_range"`, `_exclude_test_mount_option "test_dummy_encryption"`, `_require_attrs`, `_require_test`; key variables `workdir=$TEST_DIR/test-$seq`, `objsz=4194304`, `file="$workdir/file-$objsz"`, `dest="$workdir/dest-$objsz"`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L23: _begin_fstest auto quick copy_range; L30: _require_xfs_io_command "copy_range"; L31: _exclude_test_mount_option "test_dummy_encryption"; L45: _ceph_create_file_layout $file $objsz 1 $objsz; L46: _ceph_create_file_layout $dest $objsz 1 $objsz; L49: $XFS_IO_PROG -c "pwrite -S 0x61 0 $objsz" $file >> $seqres.full 2>&1; L50: $XFS_IO_PROG -c "pwrite -S 0x62 $objsz $objsz" $file >> $seqres.full 2>&1; L51: $XFS_IO_PROG -c "pwrite -S 0x63 $(($objsz * 2)) $objsz" $file >> $seqres.full 2>&1; L53: $XFS_IO_PROG -c "pwrite -S 0x64 0 $(($objsz * 3))" $dest >> $seqres.full 2>&1; L55: $XFS_IO_PROG -c "truncate 0" $dest >> $seqres.full 2>&1; L58: $XFS_IO_PROG -c "copy_range -s 0 -d 0 -l $(($objsz * 3)) $file" "$dest".

State and persistence behavior: mainly drives transient test files under TEST_DIR or SCRATCH_MNT.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands, CephFS mount, xattrs, debugfs metrics, or snapshot helpers. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ceph/002 -->
