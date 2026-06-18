<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/076 -->
# sources/test-tools/xfstests/tests/xfs/076

## Purpose
`sources/test-tools/xfstests/tests/xfs/076` is a XFS functional regression test. Verify that a filesystem with sparse inode support can allocate inodes in the event of free space fragmentation. This test is generic in nature but primarily relevant to filesystems that implement dynamic inode allocation (e.g., XFS). The test is inspired by inode allocation limitations on XFS when available free space is fragmented. XFS allocates inodes 64 at a time and thus requires an extent of length that depends on inode size (64 * isize / blksize). The test creates a small, sparse inode enabled filesystem. It fragments free space, allocates inodes to ENOSPC and then verifies that most of the available inodes (.i.e., free space) have been consumed. The `_begin_fstest` declaration is `_begin_fstest auto enospc punch prealloc`, which places the test in the `auto, enospc, punch, prealloc` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: `_consume_freesp`, `_alloc_inodes`. Required capabilities: `_require_scratch_nocheck`; `_require_scratch`; `_require_xfs_io_command "falloc"`; `_require_xfs_io_command "fpunch"`; `_require_xfs_sparse_inodes`. External and harness commands observed in the full source include `xfs_io`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo -n > $dir/$i || break`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/076.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo -n > $dir/$i || break`. The script has 113 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/076 -->
