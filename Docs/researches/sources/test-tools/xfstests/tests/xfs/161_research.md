<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/161 -->
# sources/test-tools/xfstests/tests/xfs/161

## Purpose
`sources/test-tools/xfstests/tests/xfs/161` is a quota behavior regression. Check that we can upgrade a filesystem to support bigtime and that quota timers work properly after the upgrade.  You need a quota-tools containing commit 16b60cb9e315ed for this test to run properly; v4.06 should do. The word 'projectname' was added to quota(8)'s synopsis shortly after y2038+ support was added for XFS, so we use that to decide if we're going to run this test at all. Format V5 filesystem without bigtime support and populate it Write more than one block to exceed the soft block quota limit via. The `_begin_fstest` declaration is `auto quick bigtime quota`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/quota`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_command "$XFS_ADMIN_PROG" "xfs_admin"`, `_require_command "$QUOTA_PROG" "quota"`, `_require_quota`, `_require_scratch_xfs_bigtime`, `_require_xfs_repair_upgrade bigtime`. Important external or harness commands observed in the full source include `quota`, `xfs_admin`, `xfs_quota`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; uses xfs_admin to toggle or validate filesystem feature flags; runs xfs_repair in checking or fixing mode and treats repair output as part of the oracle; uses xfs_db to inspect or perturb low-level metadata; configures or queries user/group/project quota state. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, quota accounting and grace-period metadata, on-disk metadata fields modified for corruption testing. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; quota output and timer calculations are sensitive to quota-tools versions, current time, and 32-bit time support; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/161.out`; stable progress labels including `echo "Now is after February 2222?  Expect problems."`, `echo "setting expiration to $new_expiry - $now = $expiry_delta" >> $seqres.full`, `echo "grace2 is $grace2" >> $seqres.full`, `echo "grace2 is $grace2" >> $seqres.full`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 153 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/161 -->
