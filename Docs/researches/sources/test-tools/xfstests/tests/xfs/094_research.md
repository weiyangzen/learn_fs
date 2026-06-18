<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/094 -->
# sources/test-tools/xfstests/tests/xfs/094

## Purpose
`sources/test-tools/xfstests/tests/xfs/094` is a realtime geometry/allocation regression test. Exercising the inheritable realtime inode bit. The `_begin_fstest` declaration is `_begin_fstest metadata dir ioctl auto realtime`, which places the test in the `metadata, dir, ioctl, auto, realtime` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: `_filter_realtime_flag`, `_filter_rtinherit_flag`, `_create_scratch`. Required capabilities: `_require_realtime`; `_require_scratch`. External and harness commands observed in the full source include `mkfs`, `mount`, `chattr`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "--r-- SCRATCH_MNT/testdir/$1"`; `echo "----- SCRATCH_MNT/testdir/$1"`; `echo "--t-- SCRATCH_MNT/testdir"`; `echo "----- SCRATCH_MNT/testdir"`; `echo "*** mkfs"`; `echo "failed to mkfs $SCRATCH_DEV"`; `echo "*** mount"`; `echo "failed to mount $SCRATCH_DEV"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, realtime device geometry and allocation state. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
requires a valid realtime test configuration and exact extent-size alignment. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/094.out`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "--r-- SCRATCH_MNT/testdir/$1"`, `echo "----- SCRATCH_MNT/testdir/$1"`, `echo "--t-- SCRATCH_MNT/testdir"`. The script has 82 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/094 -->
