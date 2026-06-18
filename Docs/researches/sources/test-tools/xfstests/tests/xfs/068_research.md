<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/068 -->
# sources/test-tools/xfstests/tests/xfs/068

## Purpose
`sources/test-tools/xfstests/tests/xfs/068` is a xfsdump/xfsrestore coverage test. Test out a level 0 dump/restore of a subdir to a file Use fsstress to create a larger directory structure with a mix of files Test for regression caused by c7cb51d xfs: fix error handling at xfs_inumbers The `_begin_fstest` declaration is `_begin_fstest auto stress dump`, which places the test in the `auto, stress, dump` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/dump`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`. External and harness commands observed in the full source include `mkfs`, `mount`, `fsstress`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo -n "Before: " >> $seqres.full`; `echo -n "After: " >> $seqres.full`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects dump inventory/dump files or tape state. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
dump/restore output is sensitive to inventory cleanup, timestamps, path filters, and optional tape or remote devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/068.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo -n "Before: " >> $seqres.full`, `echo -n "After: " >> $seqres.full`. The script has 46 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/068 -->
