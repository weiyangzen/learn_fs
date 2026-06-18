<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/147 -->
# sources/test-tools/xfstests/tests/xfs/147

## Purpose
`sources/test-tools/xfstests/tests/xfs/147` is a realtime geometry/allocation regression test. Make sure we validate realtime extent size alignment for fallocate modes. This is a regression test for fe341eb151ec ("xfs: ensure that fpunch, fcollapse, and finsert operations are aligned to rt extent size") The `_begin_fstest` declaration is `_begin_fstest auto quick rw realtime collapse insert unshare zero prealloc`, which places the test in the `auto, quick, rw, realtime, collapse, insert, unshare, zero, prealloc` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_realtime`; `_require_xfs_io_command "fcollapse"`; `_require_xfs_io_command "finsert"`; `_require_xfs_io_command "funshare"`; `_require_xfs_io_command "fzero"`; `_require_xfs_io_command "falloc"`. External and harness commands observed in the full source include `xfs_io`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "blksz $blksz rextsize $rextsize rextblks $rextblks" >> $seqres.full`; `echo "test $verb"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, realtime device geometry and allocation state. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
requires a valid realtime test configuration and exact extent-size alignment. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/147.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "blksz $blksz rextsize $rextsize rextblks $rextblks" >> $seqres.full`, `echo "test $verb"`. The script has 51 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/147 -->
