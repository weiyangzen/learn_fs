<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/151 -->
# sources/test-tools/xfstests/tests/xfs/151

## Purpose
`sources/test-tools/xfstests/tests/xfs/151` is a xfs_db command behavior test. Make sure the xfs_db ls command works the way the author thinks it does. This means that we can list the current directory, list an arbitrary path, and we can't list things that aren't directories. The `_begin_fstest` declaration is `_begin_fstest auto quick db`, which places the test in the `auto, quick, db` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`. Local helper surface: `filter_ls`. Required capabilities: `_require_xfs_db_command "path"`; `_require_xfs_db_command "ls"`; `_require_scratch`; `_require_xfs_has_feature "$SCRATCH_MNT" ftype`. External and harness commands observed in the full source include `xfs_db`, `mkfs`, `mount`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Format filesystem and populate"`; `echo "Manually navigate to root dir then list"`; `echo "Use path to navigate to root dir then list"`; `echo "Use path to navigate to /a then list"`; `echo "Use path to navigate to /a/b then list"`; `echo "Use path to navigate to /a/c (non-dir) then list"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/151.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Format filesystem and populate"`, `echo "Manually navigate to root dir then list"`, `echo "Use path to navigate to root dir then list"`. The script has 91 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/151 -->
