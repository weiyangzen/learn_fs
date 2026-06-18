<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/083 -->
# sources/test-tools/xfstests/tests/xfs/083

## Purpose
`sources/test-tools/xfstests/tests/xfs/083` is a XFS functional regression test. Create and populate an XFS filesystem, fuzz the metadata, then see how the kernel reacts, how xfs_repair fares in fixing the mess, and then try more kernel accesses to see if it really fixed things. The `_begin_fstest` declaration is `_begin_fstest dangerous_fuzzers punch`, which places the test in the `dangerous_fuzzers, punch` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/populate`, `. ./common/fuzzy`. Local helper surface: `scratch_repair`. Required capabilities: `_require_scratch`; `_require_attrs`; `_require_populate_commands`. External and harness commands observed in the full source include `xfs_db`, `xfs_repair`, `mkfs`, `mount`, `umount`, `chattr`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "++ fsck pass ${fsck_pass}" > "${FSCK_LOG}"`; `echo "++ allegedly fixed, reverify" >> "${FSCK_LOG}"`; `echo "++ fsck returns ${res}" >> "${FSCK_LOG}"`; `echo "++ fsck thinks we are done" >> "${FSCK_LOG}"`; `echo "+++ replaying log" >> "${FSCK_LOG}"`; `echo "+++ mount returns ${res}" >> "${FSCK_LOG}"`; `echo "+++ zeroing log" >> "${FSCK_LOG}"`; `echo "+++ returns $?" >> "${FSCK_LOG}"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects loop device mappings. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; loop/external-device cleanup must be reliable to avoid leaking mounts or loop devices; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/083.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "++ fsck pass ${fsck_pass}" > "${FSCK_LOG}"`, `echo "++ allegedly fixed, reverify" >> "${FSCK_LOG}"`, `echo "++ fsck returns ${res}" >> "${FSCK_LOG}"`. The script has 151 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/083 -->
