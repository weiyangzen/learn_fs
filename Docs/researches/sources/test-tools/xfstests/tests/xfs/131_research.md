<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/131 -->
# sources/test-tools/xfstests/tests/xfs/131

## Purpose
`sources/test-tools/xfstests/tests/xfs/131` is a XFS functional regression test. Run fsx with XFS force_zero_range error injection enabled. This is a proxy test for iomap zero range. Zero range is used in limited cases by default, such as EOF zeroing on file extension, etc. This error tag forces use of iomap zero range for fallocate zero range operations. The `_begin_fstest` declaration is `_begin_fstest auto quick zero`, which places the test in the `auto, quick, zero` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/inject`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_test`; `_require_xfs_io_error_injection "force_zero_range"`. External and harness commands observed in the full source include `xfs_io`, `fsx`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow runs XFS diagnostic or administrative tools; compares generated state to expected output or filters nondeterminism. Observable progress/output points include the expected-output oracle is mostly delegated to helper functions and companion output files. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects filesystem metadata and command output only. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/131.out`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks. The script has 26 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/131 -->
