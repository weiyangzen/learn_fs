<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/071 -->
# sources/test-tools/xfstests/tests/xfs/071

## Purpose
`sources/test-tools/xfstests/tests/xfs/071` is a XFS functional regression test. Exercise IO at large file offsets. The `_begin_fstest` declaration is `_begin_fstest rw auto`, which places the test in the `rw, auto` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: `_filter_io`, `_filter_off`, `_filter_pwrite`, `_filter_pread`, `write_block`. Required capabilities: `_require_scratch`. External and harness commands observed in the full source include `xfs_bmap`, `xfs_io`, `mkfs`, `mount`, `feature`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Writing $bytes bytes, offset is $words (direct=$direct)" | _filter_io`; `echo "Writing $bytes bytes at $location $words (direct=$direct)" >>$seqres.full`; `echo "Reading $bytes bytes (direct=$direct)" | _filter_io`; `echo "Reading $bytes bytes at $location (direct=$direct)" >>$seqres.full`; `echo | tee -a $seqres.full`; `echo`; `echo === Iterating, `expr $upperbound - $count` remains`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Writing $bytes bytes, offset is $words (direct=$direct)" | _filter_io`, `echo "Writing $bytes bytes at $location $words (direct=$direct)" >>$seqres.full`, `echo "Reading $bytes bytes (direct=$direct)" | _filter_io`. The script has 145 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/071 -->
