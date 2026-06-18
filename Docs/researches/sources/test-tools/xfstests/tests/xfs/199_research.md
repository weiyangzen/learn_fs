<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/199 -->
# sources/test-tools/xfstests/tests/xfs/199

## Purpose
`sources/test-tools/xfstests/tests/xfs/199` is a XFS fstests regression. Check that the features2 location fixups work correctly.  We check both a regular read-write mount of a filesystem and the case where the filesystem is first mounted read-only and then later remounted read-write, which is the usual case for the root filesystem. Override the default cleanup function. clear any mkfs options so that we can directly specify the options we need to be able to test the features bitmask behaviour correctly. Grab the initial configuration. This checks mkfs sets the fields properly, and. The `_begin_fstest` declaration is `mount auto quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `_cleanup`. Requirement gates: `_require_scratch`, `_require_xfs_nocrc`. Important external or harness commands observed in the full source include `mkfs`, `mount`. Notable scenario variables include `MKFS_OPTIONS=`.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; uses xfs_db to inspect or perturb low-level metadata. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, on-disk metadata fields modified for corruption testing. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/199.out`; stable progress labels including `echo "Clearing features2:"`, `echo "Clearing features2:"`, `echo "*** done"`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 71 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/199 -->
