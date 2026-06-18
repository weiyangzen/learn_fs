<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/162 -->
# sources/test-tools/xfstests/tests/xfs/162

## Purpose
`sources/test-tools/xfstests/tests/xfs/162` is a metadata repair/corruption regression. Make sure that attrs are handled properly when repair has to reset the root directory. The `_begin_fstest` declaration is `auto quick attr repair`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/populate`, `./common/fuzzy`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch_nocheck`, `_require_populate_commands`, `_require_xfs_db_command "fuzz"`. Important external or harness commands observed in the full source include primarily fstests shell helpers. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; runs xfs_repair in checking or fixing mode and treats repair output as part of the oracle; uses xfs_db to inspect or perturb low-level metadata. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, on-disk metadata fields modified for corruption testing. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/162.out`; stable progress labels including `echo "Format and populate btree attr root dir"`, `echo "Break the root directory"`, `echo "Detect bad root directory"`, `echo "Should have detected bad root dir"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 50 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/162 -->
