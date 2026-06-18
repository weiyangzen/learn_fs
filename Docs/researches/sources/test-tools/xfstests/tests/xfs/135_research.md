<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/135 -->
# sources/test-tools/xfstests/tests/xfs/135

## Purpose
`sources/test-tools/xfstests/tests/xfs/135` is a XFS functional regression test. This test verifies that the xfsprogs log formatting infrastructure works correctly for various log stripe unit values. The log is formatted with xfs_db and verified with xfs_logprint. The `_begin_fstest` declaration is `_begin_fstest auto logprint quick v2log`, which places the test in the `auto, logprint, quick, v2log` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/log`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_v2log`; `_require_xfs_db_command "logformat"`. External and harness commands observed in the full source include `xfs_db`, `mkfs`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; runs XFS diagnostic or administrative tools. Observable progress/output points include the expected-output oracle is mostly delegated to helper functions and companion output files. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects journal/log metadata. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/135.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks. The script has 38 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/135 -->
