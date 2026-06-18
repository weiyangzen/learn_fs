<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/107 -->
# sources/test-tools/xfstests/tests/xfs/107

## Purpose
`sources/test-tools/xfstests/tests/xfs/107` is a XFS functional regression test. Regression test for commit: 983d8e60f508 ("xfs: map unwritten blocks in XFS_IOC_{ALLOC,FREE}SP just like fallocate") The `_begin_fstest` declaration is `_begin_fstest auto quick prealloc`, which places the test in the `auto, quick, prealloc` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_test`; `_require_scratch`; `_require_xfs_io_command allocsp		# detect presence of ALLOCSP ioctl`; `_require_test_program allocstale`. External and harness commands observed in the full source include `xfs_io`, `mkfs`, `mount`, `allocstale`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; runs XFS diagnostic or administrative tools. Observable progress/output points include `echo "Setting up $iterations runs for block size $blksz" >> $seqres.full`; `echo Silence is golden`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/107.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Setting up $iterations runs for block size $blksz" >> $seqres.full`, `echo Silence is golden`. The script has 60 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/107 -->
