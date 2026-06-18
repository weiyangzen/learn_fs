<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/227 -->
# sources/test-tools/xfstests/tests/xfs/227

## Purpose
`sources/test-tools/xfstests/tests/xfs/227` is a XFS fstests regression. xfs_fsr QA tests run xfs_fsr over the test filesystem to give it a wide and varied set of inodes to try to defragment. This is effectively a crash/assert failure test looking for corruption induced by the kernel inadequately checking the indoes to be swapped. It also is good for validating fsr's attribute fork generation code. create freespace holes of 1-3 blocks in length This is done to ensure that defragmented files have roughly 1/3 the. The `_begin_fstest` declaration is `auto fsr`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `fragment_freespace`, `create_attrs`, `create_data`, `create_target_attr_first`, `create_target_attr_last`, `do_fsr`. Requirement gates: `_require_scratch`. Important external or harness commands observed in the full source include `xfs_bmap`, `xfs_fsr`. Notable scenario variables include `FSRXFSTEST=true xfs_fsr -d -v -C $n $targ.$i.* >> $seqres.full 2>&1`, `FSRXFSTEST=true xfs_fsr -d -v -C $n $targ.$i.* >> $seqres.full 2>&1`.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/227.out`; stable progress labels including `echo -n > $_file.$i`, `echo "user.$foo=\"0xbabe\""`, `echo "*** n == $n ***" >> $seqres.full`, `echo "--- silence is golden ---"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 189 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/227 -->
