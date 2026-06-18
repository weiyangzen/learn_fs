<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/179 -->
# sources/test-tools/xfstests/tests/xfs/179

## Purpose
`sources/test-tools/xfstests/tests/xfs/179` is a reflink and copy-on-write regression. See how well reflink handles overflowing reflink counts. This test modifies the refcount btree on the data device, so we must force rtinherit off so that the test files are created there. Set the file size to 10x the block size to guarantee that the COW writes will touch multiple blocks and exercise the refcount extent merging code.  This is necessary to catch a bug in the refcount extent merging code that handles MAXREFCOUNT edge cases. For the last COW test, write single blocks at the start, middle, and end of. The `_begin_fstest` declaration is `auto quick clone`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/attr`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_scratch_nocheck`, `_require_cp_reflink`, `_require_test_program "punch-alternating"`. Important external or harness commands observed in the full source include `mount`, `punch-alternating`, `xfs_repair`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; runs xfs_repair in checking or fixing mode and treats repair output as part of the oracle; uses xfs_db to inspect or perturb low-level metadata; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata, on-disk metadata fields modified for corruption testing. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/179.out`; stable progress labels including `echo "Format and mount"`, `echo "Create original files"`, `echo "Change reference count"`, `echo "set refcount to -4" >> $seqres.full`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 112 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/179 -->
