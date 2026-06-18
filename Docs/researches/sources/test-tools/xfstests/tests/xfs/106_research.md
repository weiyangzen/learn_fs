<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/106 -->
# sources/test-tools/xfstests/tests/xfs/106

## Purpose
`sources/test-tools/xfstests/tests/xfs/106` is a quota/accounting regression test. Exercise basic xfs_quota functionality (user/group/project quota) Use of "sync" mount option here is an attempt to get deterministic allocator behaviour. The `_begin_fstest` declaration is `_begin_fstest auto quick quota`, which places the test in the `auto, quick, quota` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`. Local helper surface: `create_files`, `clean_files`, `filter_quot`, `filter_report`, `filter_quota`, `filter_state`, `test_quot`, `test_report`, `test_quota`, `test_limit`, `test_timer`, `test_disable`, `test_enable`, `test_off`, `test_remove`, `test_state`, `test_dump`, `test_restore`, `test_xfs_quota`. Required capabilities: `_require_scratch`; `_require_xfs_quota`; `_require_user`; `_require_group`; `_require_prjquota $SCRATCH_DEV`. External and harness commands observed in the full source include `xfs_quota`, `mkfs`, `mount`, `quota`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Using type=$type id=$id" >> $seqres.full`; `echo "checking quot command (type=$type)"`; `echo "checking report command (type=$type)"`; `echo "checking quota command (type=$type)"`; `echo "checking limit command (type=$type, bsoft=$bs, bhard=$bh, isoft=$is, ihard=$ih)"`; `echo "checking timer command (type=$type)"`; `echo "checking disable command (type=$type)"`; `echo "checking enable command (type=$type)"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, quota accounting records and limits. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
quota results vary with block size, delayed allocation, mount options, and configured test users/groups/projects. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/106.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Using type=$type id=$id" >> $seqres.full`, `echo "checking quot command (type=$type)"`, `echo "checking report command (type=$type)"`. The script has 293 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/106 -->
