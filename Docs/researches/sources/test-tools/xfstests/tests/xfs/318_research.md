<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/318 -->
# sources/test-tools/xfstests/tests/xfs/318

## Purpose
Simulate free extent errors with a file write and a file remove. In this subset it exercises filesystem freeze/unfreeze behavior under stress or error injection. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick rw freeze`. It imports common/preamble, common/filter, common/inject. Local helpers are `_cleanup`. Requirement and fix gates include `_require_scratch`; `_require_error_injection`; `_require_xfs_io_error_injection "rmap_finish_one"`; `_require_freeze`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_freeze`, `mount`, `stat`, `file`, `touch`, `rm`, `sync`. Key shell state is carried in `blksz`, `blks`, `sz`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 16: `xfs_freeze -u $SCRATCH_MNT 2>/dev/null`; line 18: `rm -rf $tmp.*`; line 27: `_require_xfs_io_error_injection "rmap_finish_one"`; line 33: `echo "Format filesystem"`; line 34: `_scratch_mkfs >/dev/null 2>&1`; line 35: `_scratch_mount >> $seqres.full`; line 39: `_xfs_force_bdev data $SCRATCH_MNT`; line 41: `echo "Create files"`; line 42: `touch $SCRATCH_MNT/file1`; plus 3 further source-derived command steps.. error injection knobs: free_extent The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/318 -->
