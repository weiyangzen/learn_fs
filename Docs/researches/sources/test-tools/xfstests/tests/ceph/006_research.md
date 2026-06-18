<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ceph/006 -->
# sources/test-tools/xfstests/tests/ceph/006

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ceph/006_research.md`.

Source read: 63 lines, SHA256 prefix `5130c04380365b91`.

Purpose: FS QA Test No. 006 Test that snapshot data remains intact after punch hole operations on the original file. Override the default cleanup function.

Important APIs/types/functions: test tags `auto quick snapshot`; common harness imports `. ./common/preamble`, `. common/ceph`; requirements/fixed gates `_require_test`, `_require_xfs_io_command "fpunch"`, `_require_ceph_snapshot`, `_exclude_test_mount_option "test_dummy_encryption"`, `_fixed_by_kernel_commit xxxxxxxxxxxx \`; helper functions `_cleanup()`; key variables `workdir=$TEST_DIR/test-$seq`, `snapdir=$(_ceph_create_snapshot $workdir snap1)`, `original_md5=$(md5sum $snapdir/foo | cut -d' ' -f1)`, `snapshot_md5=$(md5sum $snapdir/foo | cut -d' ' -f1)`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L18: _ceph_remove_snapshot $workdir snap1; L24: _require_xfs_io_command "fpunch"; L25: _require_ceph_snapshot; L26: _exclude_test_mount_option "test_dummy_encryption"; L33: _ceph_remove_snapshot $workdir snap1; L37: $XFS_IO_PROG -f -c "pwrite -S 0xab 0 1048576" $workdir/foo > /dev/null; L39: snapdir=$(_ceph_create_snapshot $workdir snap1); L41: original_md5=$(md5sum $snapdir/foo | cut -d' ' -f1); L43: $XFS_IO_PROG -c "fpunch 0 65536" $workdir/foo; L44: $XFS_IO_PROG -c "fpunch 131072 65536" $workdir/foo; L45: $XFS_IO_PROG -c "fpunch 262144 65536" $workdir/foo; L46: $XFS_IO_PROG -c "fpunch 393216 65536" $workdir/foo; L51: snapshot_md5=$(md5sum $snapdir/foo | cut -d' ' -f1).

State and persistence behavior: persists snapshot roots and verifies their contents; drops page cache to force media-backed reads.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands, CephFS mount, xattrs, debugfs metrics, or snapshot helpers. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: requires privileged cache dropping and can perturb the host; has a placeholder fixed-by commit annotation; is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; matching file digests before and after remount/send/receive; visible subtest labels include 3 > /proc/sys/vm/drop_caches; FAIL: Snapshot data changed after punch hole operations; Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ceph/006 -->
