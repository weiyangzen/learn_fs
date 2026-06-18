<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/051 -->
# sources/test-tools/xfstests/tests/xfs/051

## Purpose
`sources/test-tools/xfstests/tests/xfs/051` is a log recovery/error-injection test. Simulate a buffer use after free race in XFS log recovery. The race triggers on I/O failures during log recovery. Note that this test is dangerous as it causes BUG() errors or a panic. The `_begin_fstest` declaration is `_begin_fstest shutdown auto log metadata`, which places the test in the `shutdown, auto, log, metadata` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/dmflakey`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_dm_target flakey`; `_require_xfs_sysfs debug/log_recovery_delay`. External and harness commands observed in the full source include `mkfs`, `mount`, `fsstress`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; injects corruption, I/O failure, debug hooks, or log errors. Observable progress/output points include `echo "Silence is golden."`; `echo 10 > /sys/fs/xfs/debug/log_recovery_delay`; `echo 0 > /sys/fs/xfs/debug/log_recovery_delay`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, journal/log metadata. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
depends on kernel log recovery/error-injection behavior and can expose kernel bugs or require debug facilities. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/051.out`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Silence is golden."`, `echo 10 > /sys/fs/xfs/debug/log_recovery_delay`, `echo 0 > /sys/fs/xfs/debug/log_recovery_delay`. The script has 69 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/051 -->
