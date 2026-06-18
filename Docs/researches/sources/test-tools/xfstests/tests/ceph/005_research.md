<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ceph/005 -->
# sources/test-tools/xfstests/tests/ceph/005

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ceph/005_research.md`.

Source read: 39 lines, SHA256 prefix `b749236e468d972d`.

Purpose: FS QA Test 005 Make sure statfs reports correct total size when: 1. using a directory with 'max_byte' quota as base for a mount 2. using a subdirectory of the above directory with 'max_files' quota.

Important APIs/types/functions: test tags `auto quick quota`; common harness imports `. ./common/preamble`; requirements/fixed gates `_require_scratch`, `_exclude_test_mount_option "test_dummy_encryption"`; key variables `quota=$((2 ** 30)) # 1G`, `SCRATCH_DEV_ORIG="$SCRATCH_DEV"`, `SCRATCH_DEV="$SCRATCH_DEV/quota-dir" _scratch_mount`, `SCRATCH_DEV="$SCRATCH_DEV_ORIG/quota-dir" _scratch_unmount`, `SCRATCH_DEV="$SCRATCH_DEV_ORIG/quota-dir/subdir" _scratch_mount`, `SCRATCH_DEV="$SCRATCH_DEV_ORIG/quota-dir/subdir" _scratch_unmount`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L15: _exclude_test_mount_option "test_dummy_encryption"; L17: _scratch_mount; L24: _scratch_unmount; L27: SCRATCH_DEV="$SCRATCH_DEV/quota-dir" _scratch_mount; L29: SCRATCH_DEV="$SCRATCH_DEV_ORIG/quota-dir" _scratch_unmount; L31: SCRATCH_DEV="$SCRATCH_DEV_ORIG/quota-dir/subdir" _scratch_mount; L33: SCRATCH_DEV="$SCRATCH_DEV_ORIG/quota-dir/subdir" _scratch_unmount.

State and persistence behavior: mounts and unmounts test filesystems; changes quota/qgroup accounting state.

Dependencies and integration points: Depends on xfstests common libraries, CephFS mount, xattrs, debugfs metrics, or snapshot helpers. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: quota accounting regressions can be silent until unmount or rescan.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ceph/005 -->
