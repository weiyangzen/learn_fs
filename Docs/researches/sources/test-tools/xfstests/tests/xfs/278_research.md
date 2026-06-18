<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/278 -->
# sources/test-tools/xfstests/tests/xfs/278

## Purpose
Test xfs_repair to ensure it fixes the lost+found link count at the first run. See also commit 198b747f255346bca64408875763b6ca0ed3d57d from xfsprogs tree. In this subset it exercises xfs_repair detection and correction of crafted metadata damage. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest repair auto`. It imports common/preamble, common/filter. Local helpers are `set_ifield`. Requirement and fix gates include `_require_scratch`. External tools and command surfaces visible in the source include `xfs_repair`, `mount`, `stat`, `awk`, `mkdir`, `rm`. Key shell state is carried in `DIR_INO`, `SUBDIR_INO`, `sfdir_prefix`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 21: `_scratch_mkfs >$seqres.full 2>&1`; line 22: `_scratch_mount`; line 24: `mkdir -p $SCRATCH_MNT/dir/subdir`; line 30: `_scratch_unmount`; line 32: `echo "Silence is goodness..."`; line 35: `_scratch_xfs_set_metadata_field "$1" 0 "inode $2" >> $seqres.full`; line 54: `echo "===== BEGIN of xfs_repair =====" >> $seqres.full`; line 55: `echo "" >>$seqres.full`; line 57: `_scratch_xfs_repair >> $seqres.full 2>&1`; plus 1 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/278 -->
