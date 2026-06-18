<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/287 -->
# sources/test-tools/xfstests/tests/xfs/287

## Purpose
Test to verify project quota xfs_admin, xfsdump/xfsrestore and xfs_db functionality In this subset it exercises quota accounting, dquot metadata, and quota mount mode handling; xfsdump/xfsrestore compatibility and metadata preservation; xfs_fsr defragmentation and exchangerange recovery. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto dump quota quick`. It imports common/preamble, common/quota, common/dump. Local helpers are `_cleanup`, `_print_projid`. Requirement and fix gates include `_require_xfs_quota`; `_require_scratch`; `_require_projid32bit`; `_require_projid16bit`; `_require_prjquota $SCRATCH_DEV`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_db`, `xfsdump`, `xfsrestore`, `xfs_quota`, `dd`, `mount`, `stat`, `diff`, `file`, `touch`, `mkdir`. Key shell state is carried in `dir`, `inode16a`, `inode32a`, `restore_dir`, `inode16b`, `inode32b`, `inode32v2`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 22: `rm -rf $tmp.*`; line 27: `_scratch_xfs_db -r -c "inode $1" \`; line 32: `_require_xfs_quota`; line 38: `_scratch_mkfs_xfs -i projid32bit=0 -d size=200m >> $seqres.full`; line 48: `mkdir -p $dir`; line 49: `touch $dir/{16,32}bit`; line 52: `$XFS_QUOTA_PROG -x -c "project -s -p $dir/16bit 1234" $SCRATCH_DEV \`; line 54: `$XFS_QUOTA_PROG -x -c "project -s -p $dir/32bit 2123456789" $SCRATCH_DEV \`; line 57: `echo "No 32bit project quotas:"`; plus 3 further source-derived command steps.. uses common/dump dump and restore helpers with content comparison mounts or inspects quota state and dquot accounting The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include quota state can persist through remounts and is sensitive to mount options. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/287 -->
