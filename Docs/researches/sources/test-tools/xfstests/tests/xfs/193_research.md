<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/193 -->
# sources/test-tools/xfstests/tests/xfs/193

## Purpose
`sources/test-tools/xfstests/tests/xfs/193` is a reflink and copy-on-write regression. Test fragmentation after a lot of random CoW: - Create two reflinked files.  Set extsz hint on second file. - Buffered write to random offsets to scatter CoW reservations. - Check the number of extents. The `_begin_fstest` declaration is `auto quick clone fiemap`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/reflink`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_xfs_io_command "cowextsize"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`, `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. Important external or harness commands observed in the full source include `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/193.out`; stable progress labels including `echo "Format and mount"`, `echo "Create the original files"`, `echo "Compare files"`, `echo "CoW and unmount"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 71 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/193 -->
