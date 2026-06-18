<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ceph/004 -->
# sources/test-tools/xfstests/tests/ceph/004

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ceph/004_research.md`.

Source read: 101 lines, SHA256 prefix `4dcb0f762b1cdb20`.

Purpose: FS QA Test 004 Tests a bug fix found in cephfs quotas handling. Here's a simplified testcase that *should* fail: mkdir files limit truncate files/file -s 10G setfattr limit -n ceph.quota.max_bytes -v 1048576 mv files limit/ Because we're creating a new file and truncating it, we have Fx caps and thus the truncate operation will be cached. This prevents the MDSs from updating the quota realms and thus the client will allow the above rename(2) to happen. The bug resulted in dropping support for cross quota-realms renames, reverting kernel commit dffdcd71458e ("ceph: allow rename operation under different quota realms"). So, the above test will now fail with a -EXDEV or, in the future (when we have a proper fix), with -EDQUOT. This bug was tracker here: https://tracker.ceph.com/issues/48203 Import common functions..

Important APIs/types/functions: test tags `auto quick quota`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`; requirements/fixed gates `_require_attrs`, `_require_test`, `_require_test_program "rename"`, `_require_ceph_vxattr_caps # we need to get file capabilities`; helper functions `get_ceph_caps()`, `check_Fs_caps()`; key variables `workdir=$TEST_DIR/test-$seq`, `orig1=$workdir/orig1`, `orig2=$workdir/orig2`, `file1=$orig1/file`, `file2=$orig2/file`, `dest=$workdir/dest`, `caps=`get_ceph_caps $1``, `Fs=$((1 << 8))`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `get_ceph_caps()`, `check_Fs_caps()`. Representative operation sequence: L41: _require_ceph_vxattr_caps # we need to get file capabilities; L58: get_ceph_caps(); L67: caps=`get_ceph_caps $1`; L86: $XFS_IO_PROG -f -c "truncate 10G" $file1; L92: $XFS_IO_PROG -f -c "truncate 10G" $file2.

State and persistence behavior: changes quota/qgroup accounting state.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands, CephFS mount, xattrs, debugfs metrics, or snapshot helpers. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: quota accounting regressions can be silent until unmount or rescan.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ceph/004 -->
