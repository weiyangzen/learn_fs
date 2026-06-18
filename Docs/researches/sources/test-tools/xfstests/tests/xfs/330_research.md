<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/330 -->
# sources/test-tools/xfstests/tests/xfs/330

## Purpose
Ensure that xfs_fsr handles quota correctly while defragging files. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; quota accounting, dquot metadata, and quota mount mode handling; xfs_fsr defragmentation and exchangerange recovery. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone fsr quota prealloc`. It imports common/preamble, common/filter, common/attr, common/reflink, common/quota. Local helpers are `do_repquota`. Requirement and fix gates include `_require_scratch_reflink`; `_require_cp_reflink`; `_require_xfs_io_command "falloc" # used in FSR`; `_require_command "$XFS_FSR_PROG" "xfs_fsr"`; `_require_quota`; `_require_nobody`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_fsr`, `dd`, `mount`, `stat`, `grep`, `sed`, `file`, `touch`, `mkdir`, `cp`, `rm`. Key shell state is carried in `HIDDEN_QUOTA_FILES`, `testdir`, `blksz`, `blks`, `old_nextents`, `new_nextents`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_xfs_io_command "falloc" # used in FSR`; line 21: `_require_command "$XFS_FSR_PROG" "xfs_fsr"`; line 29: `$val = '"$HIDDEN_QUOTA_FILES"';`; line 33: `rm -f "$seqres.full"`; line 35: `echo "Format and mount"`; line 36: `_scratch_mkfs > "$seqres.full" 2>&1`; line 38: `_scratch_mount >> "$seqres.full" 2>&1`; line 40: `HIDDEN_QUOTA_FILES=$(_xfs_calc_hidden_quota_files $SCRATCH_MNT)`; line 47: `mkdir "$testdir"`; plus 3 further source-derived command steps.. drives xfs_fsr defragmentation paths mounts or inspects quota state and dquot accounting creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include quota state can persist through remounts and is sensitive to mount options; shared extent and CoW accounting depends on reflink/refcount support. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/330 -->
