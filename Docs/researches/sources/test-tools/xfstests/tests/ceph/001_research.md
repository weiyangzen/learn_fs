<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ceph/001 -->
# sources/test-tools/xfstests/tests/ceph/001

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ceph/001_research.md`.

Source read: 288 lines, SHA256 prefix `a59e8c1e779b43a7`.

Purpose: FS QA Test No. ceph/001 Test remote copy operation (CEPH_OSD_OP_COPY_FROM) with several combinations of both object sizes and copy sizes. It also uses several combinations of copy ranges. For example, copying the 1st object in the src file into 1) the beginning (1st object) of dst file, 2) the end (last object) of dst file and 3) the middle of the dst file. get standard environment.

Important APIs/types/functions: test tags `auto quick copy_range`; common harness imports `. ./common/preamble`, `. common/filter`, `. common/attr`, `. common/reflink`; requirements/fixed gates `_require_debugfs`, `_require_xfs_io_command "copy_range"`, `_exclude_test_mount_option "test_dummy_encryption"`, `_require_attrs`, `_require_test`; helper functions `check_range()`, `get_copyfrom_total_copies()`, `get_copyfrom_total_size()`, `check_copyfrom_metrics()`, `run_copy_range_tests()`; key variables `workdir=$TEST_DIR/test-$seq`, `cluster_fsid=$(_ceph_get_cluster_fsid)`, `client_id=$(_ceph_get_client_id)`, `metrics_dir="$DEBUGFS_MNT/ceph/$cluster_fsid.$client_id/metrics"`, `total=$(grep copyfrom $metrics_dir/size | tr -s '[:space:]' | cut -d ' ' -f 2)`, `total=$(grep copyfrom $metrics_dir/size | tr -s '[:space:]' | cut -d ' ' -f 6)`, `sum=$(($c0+$copies))`, `sum=$(($s0+$copies*$objsz))`, `total_copies=$(get_copyfrom_total_copies)`, `total_size=$(get_copyfrom_total_size)`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `check_range()`, `get_copyfrom_total_copies()`, `get_copyfrom_total_size()`, `check_copyfrom_metrics()`, `run_copy_range_tests()`. Representative operation sequence: L14: _begin_fstest auto quick copy_range; L21: _require_debugfs; L22: _require_xfs_io_command "copy_range"; L23: _exclude_test_mount_option "test_dummy_encryption"; L31: cluster_fsid=$(_ceph_get_cluster_fsid); L32: client_id=$(_ceph_get_client_id); L91: return # skip metrics check if debugfs isn't mounted; L107: run_copy_range_tests(); L119: _ceph_create_file_layout $file $objsz 1 $objsz; L120: _ceph_create_file_layout $copy $objsz 1 $objsz; L121: _ceph_create_file_layout $dest $objsz 1 $objsz; L124: $XFS_IO_PROG -c "pwrite -S 0x61 0 $objsz" $file >> $seqres.full 2>&1; L125: $XFS_IO_PROG -c "pwrite -S 0x62 $objsz $objsz" $file >> $seqres.full 2>&1; L126: $XFS_IO_PROG -c "pwrite -S 0x63 $(($objsz * 2)) $objsz" $file >> $seqres.full 2>&1; L130: $XFS_IO_PROG -c "copy_range -s 0 -d 0 -l $(($objsz * 3)) $file" "$copy"; L131: cmp $file $copy; L135: $XFS_IO_PROG -c "pwrite -S 0x64 0 $(($objsz * 3))" $dest >> $seqres.full 2>&1; L138: $XFS_IO_PROG -c "copy_range -s 0 -d 0 -l $objsz $file" "$dest".

State and persistence behavior: edits or inspects ext metadata directly.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands, CephFS mount, xattrs, debugfs metrics, or snapshot helpers. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: byte-for-byte compare of copied or restored data; visible subtest labels include Copy whole file (3 objects):; aaaa|bbbb|cccc => aaaa|bbbb|cccc; Copy single object to beginning:; dddd|dddd|dddd => aaaa|dddd|dddd; aaaa|dddd|dddd => bbbb|dddd|dddd; bbbb|dddd|dddd => cccc|dddd|dddd.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ceph/001 -->
