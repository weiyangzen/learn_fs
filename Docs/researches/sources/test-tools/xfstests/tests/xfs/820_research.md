<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/820 -->
# sources/test-tools/xfstests/tests/xfs/820

Purpose: tests persistent quota accounting and enforcement flags when XFS metadata directories are enabled.

Important APIs, types, and functions: uses `_require_xfs_scratch_metadir`, `_require_xfs_quota`, `qerase_mkfs_options`, `confirm`, `_qmount_option`, `xfs_quota state -ugp`, `_scratch_xfs_repair`, and shutdown recovery helpers.

Control flow: the script removes quota mkfs options from the environment, formats with different persistent quota flag combinations, mounts with and without quota options, checks state, runs repair, tests odd option combinations, and validates recovery after forced shutdown and quotaoff.

State and persistence behavior: quota flag state is persisted in metadir-backed quota metadata across repair, shutdown recovery, and remounts.

Dependencies and integration points: depends on mkfs support for `uquota`, xfs_quota, metadata directories, scratch mount option manipulation, and filesystem checking.

Risks and test signals: mount options can mask persistent settings, so the helper blanks them deliberately. Signals are stable filtered quota state and clean scratch checks after recovery.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/820 -->
