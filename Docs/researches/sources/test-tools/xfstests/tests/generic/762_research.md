# sources/test-tools/xfstests/tests/generic/762


Purpose: Validates statfs/statvfs reporting when project quota limits apply to a directory tree and whole-filesystem free space changes.


Important APIs, helpers, and commands: Uses `common/quota`, `_scratch_enable_pquota`, `_qmount_option prjquota`, `_force_vfs_quota_testing`, xfs_io `statfs`/`chproj`, `setquota`, `fallocate`, and `_within_tolerance`.
 Local helper functions detected in the file include `bavail`, `blocks`, `bsize`.
 It imports `./common/filter`, `./common/preamble`, `./common/quota`.
 Capability gates include `_require_prjquota`, `_require_quota`, `_require_scratch`, `_require_xfs_io_command`.
 Regression annotations include `_fixed_by_fs_commit xfs 4b8d867ca6e2 \`.



Control flow, state, dependencies, risks, and test signals: It mounts with project quotas, captures root statfs, assigns project 55 to a directory with a limit of half available blocks, checks root vs directory blocks/bavail, consumes most global free space, writes 10 blocks inside the project, and checks statfs after each stage. State is project quota accounting, file allocations, and statfs values. Dependencies are quota tooling and project quota support. Risks are tolerance mismatches due to metadata overhead and quota activation failures. Signals are `_within_tolerance` failures and diagnostic quota/df output. Source size is 114 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
