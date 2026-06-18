<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/118 -->
# sources/test-tools/xfstests/tests/xfs/118

## Purpose
`sources/test-tools/xfstests/tests/xfs/118` is a metadata corruption and repair regression test. Test xfs_fsr's handling of 2-extent files with preallocation An error in xfs_swap_extent_forks() incorrectly set up the temporary inode's if_extents pointer to inline, leading to in-memory corruption when the temporary inode was released and torn down; i_itemp and d_ops got overwritten with zeros, which led to an oops in xfs_trans_log_inode down the fput path. Fixed upstream by proper nextents counting using ip->i_df.if_bytes not ip->i_d.di_nextents in xfs_swap_extent_forks The `_begin_fstest` declaration is `_begin_fstest auto quick fsr prealloc`, which places the test in the `auto, quick, fsr, prealloc` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_command "$XFS_FSR_PROG" "xfs_fsr"`; `_require_xfs_io_command "falloc"`. External and harness commands observed in the full source include `xfs_fsr`, `xfs_io`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Silence is golden"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, journal/log metadata. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/118.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Silence is golden"`. The script has 67 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/118 -->
