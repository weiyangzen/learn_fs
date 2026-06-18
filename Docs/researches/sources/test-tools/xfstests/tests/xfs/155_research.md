<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/155 -->
# sources/test-tools/xfstests/tests/xfs/155

## Purpose
`sources/test-tools/xfstests/tests/xfs/155` is a xfs_repair regression test. Populate a filesystem with all types of metadata, then run repair with the libxfs write failure trigger set to go after a single write.  Check that the injected error trips, causing repair to abort, that needsrepair is set on the fs, the kernel won't mount; and that a non-injecting repair run clears needsrepair and makes the filesystem mountable again. Repeat with the trip point set to successively higher numbers of writes until we hit ~200 writes or repair manages to run to completion without tripping. The `_begin_fstest` declaration is `_begin_fstest auto repair`, which places the test in the `auto, repair` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/populate`, `. ./common/filter`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_scratch_nocheck`; `_require_scratch_xfs_crc		# needsrepair only exists for v5`; `_require_populate_commands`; `_require_libxfs_debug_flag LIBXFS_DEBUG_WRITE_CRASH`; `_require_command "$TIMEOUT_PROG" timeout`. External and harness commands observed in the full source include `xfs_repair`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow mounts and unmounts scratch/test filesystems; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Setting debug hook to crash after $allowed_writes writes." >> $seqres.full`; `echo "repair failed with $res??"`; `echo "ran to completion on the first try?"`; `echo "NEEDSREPAIR should be set on corrupt fs"`; `echo "Checking filesystem one last time after $allowed_writes writes." >> $seqres.full`; `echo "Clearing NEEDSREPAIR" >> $seqres.full`; `echo "Repair failed to clear NEEDSREPAIR on the $allowed_writes writes test"`; `echo Silence is golden.`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects loop device mappings. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run; loop/external-device cleanup must be reliable to avoid leaking mounts or loop devices; xfs_repair behavior and diagnostics are part of the oracle and may change across xfsprogs versions. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/155.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Setting debug hook to crash after $allowed_writes writes." >> $seqres.full`, `echo "repair failed with $res??"`, `echo "ran to completion on the first try?"`. The script has 80 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/155 -->
