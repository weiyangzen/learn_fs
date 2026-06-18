<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/148 -->
# sources/test-tools/xfstests/tests/xfs/148

## Purpose
`sources/test-tools/xfstests/tests/xfs/148` is a metadata corruption and repair regression test. See if we catch corrupt directory names or attr names with nulls or slashes in them. The `_begin_fstest` declaration is `_begin_fstest auto quick fuzzers`, which places the test in the `auto, quick, fuzzers` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`. Local helper surface: `access_stuff`. Required capabilities: `_require_test`; `_require_attrs`; `_require_xfs_nocrc`. External and harness commands observed in the full source include `xfs_db`, `xfs_scrub`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "creating entries" >> $seqres.full`; `echo "++ ACCESSING GOOD METADATA" | tee -a $seqres.full`; `echo "++ ACCESSING BAD METADATA" | tee -a $seqres.full`; `echo "does scrub complain?" >> $seqres.full`; `echo "scrub failed to report corruption ($res)"`; `echo "does repair complain?" >> $seqres.full`; `echo "repair failed to report corruption ($res)"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects test filesystem paths/devices, loop device mappings, extended attribute forks. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; loop/external-device cleanup must be reliable to avoid leaking mounts or loop devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/148.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "creating entries" >> $seqres.full`, `echo "++ ACCESSING GOOD METADATA" | tee -a $seqres.full`, `echo "++ ACCESSING BAD METADATA" | tee -a $seqres.full`. The script has 137 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/148 -->
