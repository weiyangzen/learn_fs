<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/058 -->
# sources/test-tools/xfstests/tests/xfs/058

## Purpose
`sources/test-tools/xfstests/tests/xfs/058` is a metadata corruption and repair regression test. Ensure that xfs_db fuzz command works as advertised. The `_begin_fstest` declaration is `_begin_fstest auto quick fuzzers`, which places the test in the `auto, quick, fuzzers` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/fuzzy`. Local helper surface: `do_xfs_db`. Required capabilities: `_require_scratch_nocheck`; `_require_command "$XFS_DB_PROG" "xfs_db"`; `_require_xfs_db_command "fuzz"`. External and harness commands observed in the full source include `xfs_db`, `mkfs`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; injects corruption, I/O failure, debug hooks, or log errors; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Format"`; `echo "Allowing $cmd of corrupted data with good CRC"`; `echo "Test verb ${verb}"`; `echo "Test verb random"`; `echo "Done"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects filesystem metadata and command output only. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
intentionally corrupts metadata, so failures can be expected until repair or mount rejection checks run. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/058.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Format"`, `echo "Allowing $cmd of corrupted data with good CRC"`, `echo "Test verb ${verb}"`. The script has 54 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/058 -->
