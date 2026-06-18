<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ceph/003 -->
# sources/test-tools/xfstests/tests/ceph/003

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ceph/003_research.md`.

Source read: 101 lines, SHA256 prefix `eeb5f0cada77df0b`.

Purpose: FS QA Test No. ceph/005 Test copy_file_range with infile = outfile get standard environment.

Important APIs/types/functions: test tags `auto quick copy_range`; common harness imports `. ./common/preamble`, `. common/filter`, `. common/attr`, `. common/reflink`; requirements/fixed gates `_require_xfs_io_command "copy_range"`, `_exclude_test_mount_option "test_dummy_encryption"`, `_require_attrs`, `_require_test`; helper functions `check_range()`; key variables `workdir=$TEST_DIR/test-$seq`, `objsz=4194304`, `halfobj=$(($objsz / 2))`, `file="$workdir/file-$objsz"`, `copy="$workdir/copy-$objsz"`, `dest="$workdir/dest-$objsz"`, `backup="$file.backup"`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `check_range()`. Representative operation sequence: L10: _begin_fstest auto quick copy_range; L18: _require_xfs_io_command "copy_range"; L19: _exclude_test_mount_option "test_dummy_encryption"; L45: _ceph_create_file_layout $file $objsz 1 $objsz; L46: _ceph_create_file_layout $backup $objsz 1 $objsz; L48: $XFS_IO_PROG -c "pwrite -S 0x61 0 $objsz" $file >> $seqres.full 2>&1; L49: $XFS_IO_PROG -c "pwrite -S 0x62 $objsz $objsz" $file >> $seqres.full 2>&1; L50: $XFS_IO_PROG -c "pwrite -S 0x63 $(($objsz * 2)) $objsz" $file >> $seqres.full 2>&1; L56: $XFS_IO_PROG -c "copy_range -s 0 -d $(($objsz * 2)) -l $objsz $file" "$file"; L63: $XFS_IO_PROG -c "copy_range -s $objsz -d 0 -l $objsz $file" "$file"; L69: $XFS_IO_PROG -c "copy_range -s $(($objsz * 2)) -d $objsz -l $objsz $file" "$file"; L76: $XFS_IO_PROG -c "copy_range -s 0 -d $(($objsz + $halfobj)) -l $objsz $file" "$file"; L84: $XFS_IO_PROG -c "copy_range -s $halfobj -d $(($objsz + $halfobj)) -l $objsz $file" "$file"; L93: $XFS_IO_PROG -c "copy_range -s $halfobj -d $(($objsz * 2)) -l $objsz $file" "$file".

State and persistence behavior: mainly drives transient test files under TEST_DIR or SCRATCH_MNT.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands, CephFS mount, xattrs, debugfs metrics, or snapshot helpers. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: visible subtest labels include Copy single object to the end:; aaaa|bbbb|cccc => aaaa|bbbb|aaaa; Copy single object to the beginning:; aaaa|bbbb|aaaa => bbbb|bbbb|aaaa; Copy single object to the middle:; bbbb|bbbb|aaaa => bbbb|aaaa|aaaa.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ceph/003 -->
