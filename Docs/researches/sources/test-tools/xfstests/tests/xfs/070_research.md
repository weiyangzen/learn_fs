<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/070 -->
# sources/test-tools/xfstests/tests/xfs/070

## Purpose
`sources/test-tools/xfstests/tests/xfs/070` is a metadata corruption and repair regression test. As part of superblock verification, xfs_repair checks the primary sb and verifies all secondary sb's against the primary. In the event of geometry inconsistency, repair uses a heuristic that tracks the most frequently occurring settings across the set of N (agcount) superblocks. xfs_repair was subject to a bug that disregards this heuristic in the event that the last secondary superblock in the fs is corrupt. The side effect is an unnecessary and potentially time consuming brute force superblock scan. This is a regression test for the aforementioned xfs_repair bug. We intentionally corrupt the last superblock in the fs, run xfs_repair and verify it repairs the fs correctly. We explicitly detect a brute force scan and abort the repair to save time in the failure case. The `_begin_fstest` declaration is `_begin_fstest auto quick repair`, which places the test in the `auto, quick, repair` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/repair`. Local helper surface: `_xfs_repair_noscan`. Required capabilities: `_require_scratch_nocheck`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; compares generated state to expected output or filters nondeterminism. Observable progress/output points include the expected-output oracle is mostly delegated to helper functions and companion output files. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; loop/external-device cleanup must be reliable to avoid leaking mounts or loop devices; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/070.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks. The script has 91 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/070 -->
