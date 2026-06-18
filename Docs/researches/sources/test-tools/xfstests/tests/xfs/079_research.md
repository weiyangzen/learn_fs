<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/079 -->
# sources/test-tools/xfstests/tests/xfs/079

## Purpose
`sources/test-tools/xfstests/tests/xfs/079` is a log recovery/error-injection test. Regression test for a bug in the log record checksum mechanism of XFS. Log records are checksummed during recovery and a warning or mount failure occurs on checksum verification failure. XFS had a bug where the checksum mechanism verified different parts of a record depending on the current log buffer size. This caused spurious checksum failures when a filesystem is recovered using a different log buffer size from when the filesystem crashed. Test that log recovery succeeds with a different log buffer size from when the filesystem crashed. The `_begin_fstest` declaration is `_begin_fstest shutdown auto log quick`, which places the test in the `shutdown, auto, log, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/log`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_v2log`. External and harness commands observed in the full source include `mkfs`, `mount`, `fsstress`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Silence is golden."`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, journal/log metadata. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
depends on kernel log recovery/error-injection behavior and can expose kernel bugs or require debug facilities. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/079.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Silence is golden."`. The script has 52 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/079 -->
