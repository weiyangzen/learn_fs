<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/266 -->
# sources/test-tools/xfstests/tests/xfs/266

## Purpose
`sources/test-tools/xfstests/tests/xfs/266` is a xfsdump/xfsrestore coverage. Test incremental dumps with -D (skip unchanged dirs) Override the default cleanup function. Add a new file and append a subset of the fill'ed files So we can see if just these get dumped on an incremental Quota files are stored as special files in the dumpdir of the incremental backup.  This throws off the directory/file count reported because xfsrestore includes the dumpdir in the restore summary counts. ensure file/dir timestamps precede dump timestamp. The `_begin_fstest` declaration is `dump ioctl auto quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/dump`. Local helper surface: `_cleanup`, `_add_and_append_dumpdir_fill`, `filter_cumulative_quota_updates`. Requirement gates: `_require_scratch`. Important external or harness commands observed in the full source include `quota`, `xfsdump`, `xfsrestore`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; configures or queries user/group/project quota state; creates dump images or tape streams and verifies restore/inventory behavior. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, quota accounting and grace-period metadata, dump inventory, dump files, or tape media state. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
quota output and timer calculations are sensitive to quota-tools versions, current time, and 32-bit time support; dump/restore output is sensitive to inventory state, media splitting, timestamp filtering, and quota special files; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/266.out`; stable progress labels including `echo 'New file' >> newfile`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 73 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/266 -->
