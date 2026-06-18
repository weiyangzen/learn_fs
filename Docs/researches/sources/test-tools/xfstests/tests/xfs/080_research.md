<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/080 -->
# sources/test-tools/xfstests/tests/xfs/080

## Purpose
`sources/test-tools/xfstests/tests/xfs/080` is a XFS functional regression test. rwtest (iogen|doio) The `_begin_fstest` declaration is `_begin_fstest rw ioctl auto quick`, which places the test in the `rw, ioctl, auto, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_test`; `_require_xfs_io_command falloc	# iogen requires falloc`. External and harness commands observed in the full source include `xfs_io`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools. Observable progress/output points include `echo`; `echo Completed rwtest pass 1 successfully.`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects test filesystem paths/devices. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/080.out`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo`, `echo Completed rwtest pass 1 successfully.`. The script has 42 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/080 -->
