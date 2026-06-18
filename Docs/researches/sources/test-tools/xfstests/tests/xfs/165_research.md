<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/165 -->
# sources/test-tools/xfstests/tests/xfs/165

## Purpose
`sources/test-tools/xfstests/tests/xfs/165` is a preallocation/unwritten extent regression. Test out prealloc, direct writes and buffered read Some experimentation when looking at pv#962014 - DMF 3.7 reading incorrect data Doesn't actually reproduce the problem but it tried to :-) io tests Other test... $XFS_IO_PROG -f -c "resvsp ${off}k ${end}k" $testfile write the initial file. The `_begin_fstest` declaration is `rw pattern auto prealloc quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `_filter_io`, `_filter_bmap`. Requirement gates: `_require_test`, `_require_xfs_io_command "falloc"`. Important external or harness commands observed in the full source include `xfs_bmap`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/165.out`; stable progress labels including `echo ""`, `echo "*** offset = $offset ***"`, `echo ""`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 96 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/165 -->
