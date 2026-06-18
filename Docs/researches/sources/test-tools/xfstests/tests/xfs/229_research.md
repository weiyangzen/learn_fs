<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/229 -->
# sources/test-tools/xfstests/tests/xfs/229

## Purpose
`sources/test-tools/xfstests/tests/xfs/229` is a XFS fstests regression. Check for file corruption when using the extent size hint on the normal data subvolume. http://oss.sgi.com/bugzilla/show_bug.cgi?id=874 Based on a bug report and testcase from Geoffrey Wehrman <gwehrman@sgi.com>. Override the default cleanup function. Create the test directory Per-directory extent size hints aren't particularly useful for files that are created on the realtime section.  Force the test file to be created on. The `_begin_fstest` declaration is `auto rw`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`. Local helper surface: `_cleanup`. Requirement gates: `_require_test`, `_require_fs_space $TDIR 3200000`. Important external or harness commands observed in the full source include primarily fstests shell helpers. Notable scenario variables include `TDIR="${TEST_DIR}/t_holes"`, `NFILES="10"`, `EXTSIZE="256k"`.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/229.out`; stable progress labels including `echo "generating ${NFILES} files"`, `echo "comparing files"`, `echo "got ${errcnt} errors"`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 71 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/229 -->
