<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/110 -->
# sources/test-tools/xfstests/tests/xfs/110

## Purpose
`sources/test-tools/xfstests/tests/xfs/110` is a xfs_repair regression test. Incorrect dir2 freetab warning case from Masanori Tsuda. The `_begin_fstest` declaration is `_begin_fstest repair auto`, which places the test in the `repair, auto` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`. External and harness commands observed in the full source include `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo > $SCRATCH_MNT/test/${STR1}${STR2}${STR3}${I}`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/110.out`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo > $SCRATCH_MNT/test/${STR1}${STR2}${STR3}${I}`. The script has 58 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/110 -->
