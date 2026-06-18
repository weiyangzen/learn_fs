<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/197 -->
# sources/test-tools/xfstests/tests/xfs/197

## Purpose
`sources/test-tools/xfstests/tests/xfs/197` is a XFS fstests regression. Check that d_off can be represented in a 32 bit long type without truncation.  Note that this test will always succeed on a 64 bit systems where there is no smaller off_t. Based on a testcase from John Stanley <jpsinthemix@verizon.net>. http://oss.sgi.com/bugzilla/show_bug.cgi?id=808 Override the default cleanup function. The `_begin_fstest` declaration is `dir auto quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `_cleanup`. Requirement gates: `_require_test`. Important external or harness commands observed in the full source include primarily fstests shell helpers. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow runs a linear fstests shell scenario after requirement gating. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/197.out`; stable progress labels including `echo "*** done"`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 42 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/197 -->
