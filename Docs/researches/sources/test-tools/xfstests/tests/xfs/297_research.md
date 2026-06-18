<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/297 -->
# sources/test-tools/xfstests/tests/xfs/297

## Purpose
Test freeze/unfreeze file system randomly under fsstress Regression test for commit: 437a255 xfs: fix direct IO nested transaction deadlock. In this subset it exercises filesystem freeze/unfreeze behavior under stress or error injection; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto freeze`. It imports common/preamble, common/filter. Local helpers are `_cleanup`. Requirement and fix gates include `_require_scratch`; `_require_freeze`. External tools and command surfaces visible in the source include `fsstress`, `xfs_freeze`, `mount`, `stat`, `file`, `mkdir`, `rm`, `sync`. Key shell state is carried in `logblks`, `STRESS_DIR`, `LOOP`, `TIMEOUT`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 18: `xfs_freeze -u $SCRATCH_MNT 2>/dev/null`; line 21: `rm -f $tmp.*`; line 30: `logblks=$(_scratch_find_xfs_min_logblocks -d agcount=16,su=256k,sw=12 -l su=256k)`; line 31: `_scratch_mkfs_xfs -d agcount=16,su=256k,sw=12 -l su=256k,size=${logblks}b >/dev/null 2>&1`; line 32: `_scratch_mount`; line 35: `mkdir -p $STRESS_DIR`; line 39: `_run_fsstress_bg -d $STRESS_DIR -f sync=0 -n 1000 -p 1000 $FSSTRESS_AVOID`; line 42: `echo "Start freeze/unfreeze randomly" | tee -a $seqres.full`; line 44: `while [ $LOOP -gt 0 ];do`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include error-injection timing and shutdown/recovery behavior are kernel-sensitive; stress/race coverage is timing-sensitive and can expose hangs rather than clean assertion failures. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/297 -->
