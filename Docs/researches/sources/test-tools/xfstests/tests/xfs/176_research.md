<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/176 -->
# sources/test-tools/xfstests/tests/xfs/176

## Purpose
`sources/test-tools/xfstests/tests/xfs/176` is a online grow/shrink regression. Ensure that online shrink does not let us shrink the fs such that the end of the filesystem is now in the middle of a sparse inode cluster. Figure out the next possible inode number after the log, since we can't shrink or relocate the log consume nearly all available space (leave ~1MB) Allocate inodes in a directory until failure. Find a sparse inode cluster after logend_agno/logend_agino. Calculate the fs inode chunk size based on the inode size and fixed 64-inode. The `_begin_fstest` declaration is `auto quick shrinkfs prealloc punch`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `convert_units`, `_consume_freesp`, `_alloc_inodes`, `find_sparse_clusters`. Requirement gates: `_require_scratch`, `_require_xfs_sparse_inodes`, `_require_scratch_xfs_shrink`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`. Important external or harness commands observed in the full source include `mkfs`. Notable scenario variables include `XFS_INODES_PER_CHUNK=64`, `CHUNK_SIZE=$((isize * XFS_INODES_PER_CHUNK))`.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; uses xfs_db to inspect or perturb low-level metadata; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, loop devices and loop-mounted images, on-disk metadata fields modified for corruption testing. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; loop-device setup and teardown must be exact to avoid leaked mounts or stale devices; online grow/shrink cases depend on free-space geometry and can skip or fail if ENOSPC behavior changes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/176.out`; stable progress labels including `echo -n > $dir/$i || break`, `echo clusters >> $seqres.full`, `echo "/save inode comes after target cluster, test may fail"`, `echo "Hope to fail at shrinking to $new_size" >> $seqres.full`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 188 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/176 -->
