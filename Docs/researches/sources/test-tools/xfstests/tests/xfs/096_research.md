<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/096 -->
# sources/test-tools/xfstests/tests/xfs/096

## Purpose
`sources/test-tools/xfstests/tests/xfs/096` is a quota/accounting regression test. test xfs_quota state command (XFS v4 version) The `_begin_fstest` declaration is `_begin_fstest auto quick quota`, which places the test in the `auto, quick, quota` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`. Local helper surface: `option_string`, `filter_quota_state`, `filter_quota_state2`, `test_all_state`. Required capabilities: `_require_scratch`; `_require_xfs_quota`; `_require_xfs_nocrc`. External and harness commands observed in the full source include `xfs_quota`, `mkfs`, `mount`, `quota`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo $OPT`; `echo "== Options: $OPTIONS =="`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, quota accounting records and limits. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
quota results vary with block size, delayed allocation, mount options, and configured test users/groups/projects; requires a valid realtime test configuration and exact extent-size alignment. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/096.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo $OPT`, `echo "== Options: $OPTIONS =="`. The script has 77 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/096 -->
