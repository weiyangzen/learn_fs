<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/262 -->
# sources/test-tools/xfstests/tests/xfs/262

## Purpose
`sources/test-tools/xfstests/tests/xfs/262` is a metadata repair/corruption regression. Copy xfs_scrub to the scratch device, then run xfs_scrub in forced repair mode (which will rebuild the data forks of the running scrub executable and libraries!) to see what happens. xfs_scrub will turn on error injection itself. The `_begin_fstest` declaration is `fuzzers scrub online_repair`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/fuzzy`, `./common/inject`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_command "$LDD_PROG" ldd`, `_require_scrub`, `_require_scratch`, `_require_xfs_io_error_injection "force_repair"`, `_require_scratch_xfs_scrub`. Important external or harness commands observed in the full source include `xfs_scrub`. Notable scenario variables include `LD_LIBRARY_PATH=$SCRATCH_MNT $LDD_PROG $SCRATCH_MNT/xfs_scrub >> $seqres.full`, `XFS_SCRUB_FORCE_REPAIR=1 LD_LIBRARY_PATH=$SCRATCH_MNT $SCRATCH_MNT/xfs_scrub -dTv $SCRATCH_MNT >> $seqres.full`.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, on-disk metadata fields modified for corruption testing. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/262.out`; stable progress labels including `echo "Format and populate"`, `echo "Force online repairs"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 44 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/262 -->
