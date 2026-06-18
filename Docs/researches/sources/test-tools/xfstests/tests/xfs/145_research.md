<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/145 -->
# sources/test-tools/xfstests/tests/xfs/145

## Purpose
`sources/test-tools/xfstests/tests/xfs/145` is a quota/accounting regression test. Regression test for failing to undo delalloc quota reservations when changing project id but we fail some other part of FSSETXATTR validation.  If we fail the test, we trip debugging assertions in dmesg.  This is a regression test for commit 1aecf3734a95 ("xfs: fix chown leaking delalloc quota blocks when fssetxattr fails"). The `_begin_fstest` declaration is `_begin_fstest auto quick quota`, which places the test in the `auto, quick, quota` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/quota`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_command "$FILEFRAG_PROG" filefrag`; `_require_test_program "chprojid_fail"`; `_require_quota`; `_require_scratch`; `_require_prjquota $SCRATCH_DEV`. External and harness commands observed in the full source include `mkfs`, `mount`, `filefrag`, `quota`, `chprojid_fail`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Format filesystem" | tee -a $seqres.full`; `echo "Run test program"`; `echo "file didn't get delalloc extents, test invalid?"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, quota accounting records and limits, extended attribute forks. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
quota results vary with block size, delayed allocation, mount options, and configured test users/groups/projects. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/145.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Format filesystem" | tee -a $seqres.full`, `echo "Run test program"`, `echo "file didn't get delalloc extents, test invalid?"`. The script has 57 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/145 -->
