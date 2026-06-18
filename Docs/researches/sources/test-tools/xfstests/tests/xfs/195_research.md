<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/195 -->
# sources/test-tools/xfstests/tests/xfs/195

## Purpose
`sources/test-tools/xfstests/tests/xfs/195` is a xfsdump/xfsrestore coverage. Make sure the chattr dump flag gets picked up by xfsdump without a sync http://oss.sgi.com/bugzilla/show_bug.cgi?id=340 Override the default cleanup function. Perform a level 0 dump that respects the chattr dump exclude flag, and grep the output for the inode number we expect / do not expect to be skipped Only dump a subtree so we get away with a single partition for the subtree to be dumped and the dump file. The `_begin_fstest` declaration is `ioctl dump auto quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `_cleanup`, `_do_dump`. Requirement gates: `_require_test`, `_require_user`, `_require_command "$XFSDUMP_PROG" xfsdump`. Important external or harness commands observed in the full source include `chattr`, `xfsdump`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow creates dump images or tape streams and verifies restore/inventory behavior. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, dump inventory, dump files, or tape media state. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
dump/restore output is sensitive to inventory state, media splitting, timestamp filtering, and quota special files; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/195.out`; stable progress labels including `echo "Preparing subtree"`, `echo "No dump exclude flag set (should not be skipped)"`, `echo "Dump exclude flag set, but no sync yet (should be skipped)"`, `echo "Dump exclude flag set, after sync (should be skipped)"`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 64 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/195 -->
