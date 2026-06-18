<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/142 -->
# sources/test-tools/xfstests/tests/xfs/142

## Purpose
`sources/test-tools/xfstests/tests/xfs/142` is a realtime geometry/allocation regression test. This is a regression test for commit d0c20d38af13 "xfs: fix xfs_bmap_validate_extent_raw when checking attr fork of rt files", which fixes the bmap record validator so that it will not check the attr fork extent mappings of a realtime file against the size of the realtime volume. The `_begin_fstest` declaration is `_begin_fstest auto quick rw attr realtime`, which places the test in the `auto, quick, rw, attr, realtime` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_realtime`. External and harness commands observed in the full source include `xfs_bmap`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; runs XFS diagnostic or administrative tools; uses loop, realtime, external log, idmapped, or reflink devices. Observable progress/output points include `echo Silence is golden.`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, extended attribute forks, realtime device geometry and allocation state. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
requires a valid realtime test configuration and exact extent-size alignment. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/142.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo Silence is golden.`. The script has 42 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/142 -->
