<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/078 -->
# sources/test-tools/xfstests/tests/xfs/078

## Purpose
`sources/test-tools/xfstests/tests/xfs/078` is a online growfs behavior test. Check several growfs corner cases The `_begin_fstest` declaration is `_begin_fstest growfs auto quick`, which places the test in the `growfs, auto, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: `_filter_io`, `_grow_loop`. Required capabilities: `_require_test`; `_require_loop`; `_require_xfs_io_command "truncate"`. External and harness commands observed in the full source include `xfs_io`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "*** create loop mount point"`; `echo`; `echo "=== GROWFS (from $original to $new_size, $bsize blocksize)"`; `echo "*** mkfs loop file (size=$original)"`; `echo "*** extend loop file"`; `echo "*** mount loop filesystem"`; `echo "*** grow loop filesystem"`; `echo "*** unmount"`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects test filesystem paths/devices, loop device mappings. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
loop/external-device cleanup must be reliable to avoid leaking mounts or loop devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/078.out`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "*** create loop mount point"`, `echo`, `echo "=== GROWFS (from $original to $new_size, $bsize blocksize)"`. The script has 136 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/078 -->
