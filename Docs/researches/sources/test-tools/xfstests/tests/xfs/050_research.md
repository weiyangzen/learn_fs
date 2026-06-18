<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/050 -->
# sources/test-tools/xfstests/tests/xfs/050

## Purpose
`sources/test-tools/xfstests/tests/xfs/050` is a quota/accounting regression test. Exercises basic XFS quota functionality uquota, gquota, uqnoenforce, gqnoenforce, pquota, pqnoenforce The `_begin_fstest` declaration is `_begin_fstest quota auto quick`, which places the test in the `quota, auto, quick` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`. Local helper surface: `_filter_and_check_blks`, `_exercise`. Required capabilities: `_require_scratch`; `_require_xfs_quota`. External and harness commands observed in the full source include `xfs_quota`, `mkfs`, `mount`, `quota`, `repquota`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Using type=$type id=$id" >>$seqres.full`; `echo`; `echo "*** report no quota settings" | tee -a $seqres.full`; `echo "*** report initial settings" | tee -a $seqres.full`; `echo "ls -l $SCRATCH_MNT" >>$seqres.full`; `echo "*** push past the soft inode limit" | tee -a $seqres.full`; `echo "*** push past the soft block limit" | tee -a $seqres.full`; `echo "*** push past the hard inode limit (expect EDQUOT)" | tee -a $seqres.full`. It installs a custom `_cleanup` to tear down mounts/devices and remove temporary files.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, quota accounting records and limits. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
quota results vary with block size, delayed allocation, mount options, and configured test users/groups/projects. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/050.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Using type=$type id=$id" >>$seqres.full`, `echo`, `echo "*** report no quota settings" | tee -a $seqres.full`. The script has 201 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/050 -->
