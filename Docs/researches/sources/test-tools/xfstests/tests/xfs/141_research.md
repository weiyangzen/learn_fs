<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/141 -->
# sources/test-tools/xfstests/tests/xfs/141

## Purpose
`sources/test-tools/xfstests/tests/xfs/141` is a log recovery/error-injection test. Use the XFS log record CRC error injection mechanism to test torn writes to the log. The error injection mechanism writes an invalid CRC and shuts down the filesystem. The test verifies that a subsequent remount recovers the log and that the filesystem is consistent. Note that this test requires a DEBUG mode kernel. The `_begin_fstest` declaration is `_begin_fstest auto log metadata`, which places the test in the `auto, log, metadata` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/inject`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_xfs_io_error_injection "log_bad_crc"`; `_require_scratch`. External and harness commands observed in the full source include `xfs_io`, `mkfs`, `mount`, `fsstress`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors. Observable progress/output points include `echo "Silence is golden."`; `echo iteration $i log_badcrc_factor: $factor >> $seqres.full 2>&1`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, journal/log metadata. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
depends on kernel log recovery/error-injection behavior and can expose kernel bugs or require debug facilities. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/141.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Silence is golden."`, `echo iteration $i log_badcrc_factor: $factor >> $seqres.full 2>&1`. The script has 52 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/141 -->
