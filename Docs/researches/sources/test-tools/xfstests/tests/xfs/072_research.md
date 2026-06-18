<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/072 -->
# sources/test-tools/xfstests/tests/xfs/072

## Purpose
`sources/test-tools/xfstests/tests/xfs/072` is a XFS functional regression test. Check some unwritten extent boundary conditions The `_begin_fstest` declaration is `_begin_fstest rw auto prealloc quick`, which places the test in the `rw, auto, prealloc, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_xfs_io_command "falloc"`. External and harness commands observed in the full source include `xfs_io`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools. Observable progress/output points include `echo Silence is golden`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/072.out`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo Silence is golden`. The script has 56 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/072 -->
