<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/305 -->
# sources/test-tools/xfstests/tests/xfs/305

## Purpose
Test to verify that turn group/project quotas off while fsstress and user quotas are left on. In this subset it exercises quota accounting, dquot metadata, and quota mount mode handling. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quota`. It imports common/preamble, common/filter, common/quota. Local helpers are `_exercise`. Requirement and fix gates include `_require_scratch`; `_require_xfs_quota`. External tools and command surfaces visible in the source include `fsstress`, `xfs_quota`, `mount`, `stat`, `mkdir`. Key shell state is carried in `QUOTA_DIR`, `type`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_xfs_quota`; line 22: `_scratch_mkfs_xfs -m crc=1 >/dev/null 2>&1`; line 33: `mkdir -p $QUOTA_DIR`; line 35: `_run_fsstress_bg -d $QUOTA_DIR -n 1000000 -p 100`; line 37: `$XFS_QUOTA_PROG -x -c "disable -$type" $SCRATCH_DEV`; line 42: `echo "*** turn off group quotas"`; line 44: `echo "*** done"`; line 46: `echo "*** turn off project quotas"`; line 48: `echo "*** done"`; plus 2 further source-derived command steps.. mounts or inspects quota state and dquot accounting The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include quota state can persist through remounts and is sensitive to mount options; stress/race coverage is timing-sensitive and can expose hangs rather than clean assertion failures. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/305 -->
