<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/073 -->
# sources/test-tools/xfstests/tests/xfs/073

## Purpose
`sources/test-tools/xfstests/tests/xfs/073` is a XFS functional regression test. Test xfs_copy The `_begin_fstest` declaration is `_begin_fstest copy auto`, which places the test in the `copy, auto` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`. Local helper surface: `_filter_copy`, `_filter_path`, `_populate_scratch`, `_verify_copy`. Required capabilities: `_require_test`; `_require_attrs`; `_require_xfs_copy`; `_require_scratch`; `_require_loop`. External and harness commands observed in the full source include `xfs_copy`, `mkfs`, `mount`, `fill2attr`, `fill2fs`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo $SCRATCH_MNT/big+attr | $here/src/fill2attr`; `echo checking new image`; `echo mounting new image on loopback`; `echo retrying mount with nouuid option >>$seqres.full`; `echo mount failed - evil!`; `echo comparing new image files to old`; `echo comparing new image directories to old`; `echo comparing new image geometry to old`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, test filesystem paths/devices, loop device mappings. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
loop/external-device cleanup must be reliable to avoid leaking mounts or loop devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/073.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo $SCRATCH_MNT/big+attr | $here/src/fill2attr`, `echo checking new image`, `echo mounting new image on loopback`. The script has 161 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/073 -->
