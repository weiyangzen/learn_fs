<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/114 -->
# sources/test-tools/xfstests/tests/xfs/114

## Purpose
`sources/test-tools/xfstests/tests/xfs/114` is a reflink/refcount stress test. Make sure that we can handle insert-range followed by collapse-range. In particular, make sure that fcollapse works for rmap when the extents on either side of the collapse area are mergeable. The `_begin_fstest` declaration is `_begin_fstest auto quick clone rmap collapse insert prealloc`, which places the test in the `auto, quick, clone, rmap, collapse, insert, prealloc` fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`. Local helper surface: no local helper functions beyond optional `_cleanup`. Required capabilities: `_require_test_program "punch-alternating"`; `_require_cp_reflink`; `_require_scratch_reflink`; `_require_xfs_scratch_rmapbt`; `_require_xfs_io_command "falloc"`; `_require_xfs_io_command "fcollapse"`; `_require_xfs_io_command "finsert"`; `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. External and harness commands observed in the full source include `xfs_io`, `mkfs`, `mount`, `punch-alternating`.

## Control Flow
After sourcing `common/preamble`, the script declares the fstest, imports common helpers, performs requirement gating, prepares scratch/test state, then executes the scenario. The main flow formats scratch filesystems; mounts and unmounts scratch/test filesystems; creates or mutates files, directories, links, xattrs, ACLs, or quotas; runs XFS diagnostic or administrative tools; uses loop, realtime, external log, idmapped, or reflink devices; compares generated state to expected output or filters nondeterminism. Observable progress/output points include `echo "Format and mount"`; `echo "Create some files"`; `echo "Insert and write file range"`; `echo "f1 bmap" >> $seqres.full`; `echo "f2 bmap" >> $seqres.full`; `echo "fsmap" >> $seqres.full`; `echo "Remount"`; `echo "Collapse file"`. It relies primarily on the default fstests cleanup path.

## State And Persistence Behavior
The test mutates or inspects scratch filesystem/device contents. Persistent state is deliberately confined to fstests scratch/test devices, temporary files under `$tmp.*`, generated dump/image files, and diagnostic logs such as `$seqres.full`; successful completion leaves the harness to unmount, check, or repair as appropriate.

## Dependencies And Integration Points
Integration is through the fstests XFS harness, especially the imported common modules and `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, and `$seqres.full`. The case also integrates with the named XFS userspace tools and feature gates so unsupported kernels, filesystems, devices, users, or tool versions are skipped instead of producing false failures.

## Risks
relies on fstests environment variables, scratch/test device hygiene, and filtered golden output remaining stable. Changes to filters, helper semantics, or xfsprogs/kernel diagnostics can affect the golden output even when filesystem behavior is unchanged.

## Test Signals
Primary signals are companion golden output `sources/test-tools/xfstests/tests/xfs/114.out`; diagnostic logging to `$seqres.full`; harness failures via `_fail`, `_notrun`, command exit status, and post-test fs checks; stable progress labels such as `echo "Format and mount"`, `echo "Create some files"`, `echo "Insert and write file range"`. The script has 107 source lines, so the behavior is small enough to audit as a single fstests scenario but still depends on the shared harness for setup, filtering, and final filesystem health checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/114 -->
