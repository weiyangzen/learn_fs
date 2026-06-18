<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/137 -->
# sources/test-tools/xfstests/tests/xfs/137

## Purpose
`sources/test-tools/xfstests/tests/xfs/137` is a XFS functional regression test. XFS v5 supers carry an LSN in various on-disk structures to track when associated metadata was last written to disk. These metadata LSNs must always be behind the current LSN as dictated by the log to ensure log recovery correctness after a potential crash. This test uses xfs_db to intentionally put the current LSN behind metadata LSNs and verifies that the kernel and xfs_repair detect the problem. The `_begin_fstest` declaration is `_begin_fstest auto metadata v2log`, which places the test in the `auto, metadata, v2log` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_scratch_xfs_crc`; `_require_xfs_db_command "logformat"`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`, `mount`, `fsstress`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; runs XFS diagnostic or administrative tools. Observable progress/output points include `echo mount failure detected`; `echo repair failure detected`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, journal/log metadata. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/137.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo mount failure detected`, `echo repair failure detected`. The script has 57 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/137 -->
