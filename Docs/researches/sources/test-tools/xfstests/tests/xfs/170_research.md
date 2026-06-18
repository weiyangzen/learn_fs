<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/170 -->
# sources/test-tools/xfstests/tests/xfs/170

## Purpose
`sources/test-tools/xfstests/tests/xfs/170` is a reflink and copy-on-write regression. FSQA Test No. 170 Check the filestreams allocator is doing its job. Multi-file data streams should always write into seperate AGs. test small stream, multiple I/O per file, 30s timeout This test checks that the filestreams allocator never allocates space in any given AG into more than one stream when there's plenty of space on the filesystem.  Newer feature sets (e.g. reflink) have increased the size of the log for small filesystems, so we make sure there's one more AG than. The `_begin_fstest` declaration is `rw filestreams auto quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/filestreams`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch`. Important external or harness commands observed in the full source include primarily fstests shell helpers. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/170.out`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 39 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/170 -->
