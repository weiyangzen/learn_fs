<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/055 -->
# sources/test-tools/xfstests/tests/ext4/055

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/055_research.md`.

Source read: 58 lines, SHA256 prefix `17858b6a6929750d`.

Purpose: FS QA Test 055 The preceding illegal memory access problem occurs due to tampering with the quota index information in the image. Regression test for kernel commit 9bf3d2033129 quota: check block number when reading the block in quota file commit d0e36a62bd4c quota: correct error number in free_dqentry() The test is based on a testcase from Zhang Yi <yi.zhang@huawei.com>..

Important APIs/types/functions: test tags `auto quota`; common harness imports `. ./common/preamble`, `. ./common/quota`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch_nocheck`, `_require_user fsgqa`, `_require_user fsgqa2`, `_require_command "$DEBUGFS_PROG" debugfs`, `_require_quota`, `_exclude_scratch_mount_option dax`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L23: _require_scratch_nocheck; L26: _require_command "$DEBUGFS_PROG" debugfs; L32: _exclude_scratch_mount_option dax; L33: _scratch_mkfs "-F -O quota -b 1024" > $seqres.full 2>&1; L37: $DEBUGFS_PROG -w -R "zap_block -o 0 -l 1 -p 6 -f <3> 1" $SCRATCH_DEV >> $seqres.full 2>&1; L38: _scratch_mount >> $seqres.full 2>&1.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; changes quota/qgroup accounting state; edits or inspects ext metadata directly.

Dependencies and integration points: Depends on xfstests common libraries, e2fsprogs debug/fsck utilities, quota userspace tools. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: bypasses normal scratch checking because corruption is intentional; quota accounting regressions can be silent until unmount or rescan.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/055 -->
