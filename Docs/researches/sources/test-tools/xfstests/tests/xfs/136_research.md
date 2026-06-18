<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/136 -->
# sources/test-tools/xfstests/tests/xfs/136

## Purpose
`sources/test-tools/xfstests/tests/xfs/136` is a XFS functional regression test. Test the attr2 code Let's look, xfs_db, at the inode and its literal area for the extents and the attributes The `_begin_fstest` declaration is `_begin_fstest attr2`, which places the test in the `attr2` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`. Local helper surface: `_filter`, `add_eas`, `rm_eas`, `do_extents`, `_print_inode`, `_print_inode_u`, `_print_inode_a`, `_test_add_eas`, `_test_add_extents`, `_test_extents_eas`, `_test_eas_extents`, `_test_initial_sf_ea`. Required capabilities: `_require_scratch`; `_require_attrs`. External and harness commands observed in the full source include `xfs_db`, `mkfs`, `mount`, `makeextents`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "inum=$inum"`; `echo ""; echo "** add $start..$end EAs **"`; `echo ""; echo "** rm $start..$end EAs **"`; `echo ""; echo "** $num extents **"`; `echo "--- extents: $i ---"`; `echo ""`; `echo "*** Extent differences before and after EAs added ***"`; `echo "Data extents magically changed"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents, loop device mappings. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
loop/external-device cleanup must be reliable to avoid leaking mounts or loop devices. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/136.out`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "inum=$inum"`, `echo ""; echo "** add $start..$end EAs **"`, `echo ""; echo "** rm $start..$end EAs **"`. The script has 328 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/136 -->
