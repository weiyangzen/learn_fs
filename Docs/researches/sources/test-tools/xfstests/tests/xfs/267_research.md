<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/267 -->
# sources/test-tools/xfstests/tests/xfs/267

## Purpose
`sources/test-tools/xfstests/tests/xfs/267` is a xfsdump/xfsrestore coverage. Test xfsdump with a file spanning multiple media files. Override the default cleanup function. create a 40 MiB file with an extended attr. xfsdump writes file data in "extent groups", currently 16 MiB in size. After writing an extent group or finishing a file, xfsdump will start a new media file if it is over the suggested size. With a single 40 MiB file and using a suggested media file size of 12 MiB below, this dump will be contained in 3 media files. The `_begin_fstest` declaration is `dump ioctl tape`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/dump`, `./common/attr`. Local helper surface: `_cleanup`, `_create_files`. Requirement gates: `_require_tape $TAPE_DEV`, `_require_attrs trusted`, `_require_scratch`. Important external or harness commands observed in the full source include `xfsdump`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; creates dump images or tape streams and verifies restore/inventory behavior. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, dump inventory, dump files, or tape media state. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
dump/restore output is sensitive to inventory state, media splitting, timestamp filtering, and quota special files; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/267.out`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 61 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/267 -->
