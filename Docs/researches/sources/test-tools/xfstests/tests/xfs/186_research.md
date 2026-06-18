<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/186 -->
# sources/test-tools/xfstests/tests/xfs/186

## Purpose
`sources/test-tools/xfstests/tests/xfs/186` is a XFS fstests regression. Test out: pv#979606: xfs bug in going from attr2 back to attr1 Test bug in going from attr2 back to attr1 where xfs (due to xfs_attr_shortform_bytesfit) would reset the di_forkoff to the m_offset instead of leaving the di_forkoff alone as was intended. We create enough dirents to push us past m_attroffset, and create an EA so we have a fork offset. The `_begin_fstest` declaration is `attr auto quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/attr`. Local helper surface: `_create_dirents`, `_create_eas`, `_rmv_eas`, `_filter_inode`, `_filter_version`, `_print_inode`, `_do_eas`, `_do_dirents`, `_changeto_attr1`. Requirement gates: `_require_scratch`, `_require_attrs`, `_require_attr_v1`. Important external or harness commands observed in the full source include `mkfs`, `xfs_add_shortform_bytesfit`, `xfs_attr_shortform_bytesfit`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; uses xfs_db to inspect or perturb low-level metadata. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, on-disk metadata fields modified for corruption testing. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/186.out`; stable progress labels including `echo ""`, `echo "================================="`, `echo "================================="`, `echo ""`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 167 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/186 -->
