<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/146 -->
# sources/test-tools/xfstests/tests/xfs/146

## Purpose
`sources/test-tools/xfstests/tests/xfs/146` is a metadata corruption and repair regression test. This is a regression test for commit 2a6ca4baed62 ("xfs: make sure the rt allocator doesn't run off the end") which fixes an overflow error in the _near realtime allocator.  If the rt bitmap ends exactly at the end of a block and the number of rt extents is large enough to allow an allocation request larger than the maximum extent size, it's possible that during a large allocation request, the allocator will fail to constrain maxlen on the second run through the loop, and the rt bitmap range check will run right off the end of the rtbitmap file.  When this happens, xfs triggers a verifier error and returns EFSCORRUPTED. The `_begin_fstest` declaration is `_begin_fstest auto quick rw realtime prealloc`, which places the test in the `auto, quick, rw, realtime, prealloc` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch`; `_require_realtime`; `_require_xfs_io_command "falloc"`; `_require_test_program "punch-alternating"`. External and harness commands observed in the full source include `xfs_io`, `mkfs`, `mount`, `punch-alternating`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; runs XFS diagnostic or administrative tools; uses loop, realtime, external log, idmapped, or reflink devices. Observable progress/output points include `echo "blksz $blksz rextsize $rextsize rextblks $rextblks" >> $seqres.full`; `echo "rtsize1 $rtsize1 rtsize2 $rtsize2 rtsize $rtsize" >> $seqres.full`; `echo "rt size will be $rtsize" >> $seqres.full`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, loop device mappings, realtime device geometry and allocation state. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; requires a valid realtime test configuration and exact extent-size alignment; loop/external-device cleanup must be reliable to avoid leaking mounts or loop devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/146.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "blksz $blksz rextsize $rextsize rextblks $rextblks" >> $seqres.full`, `echo "rtsize1 $rtsize1 rtsize2 $rtsize2 rtsize $rtsize" >> $seqres.full`, `echo "rt size will be $rtsize" >> $seqres.full`. The script has 86 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/146 -->
