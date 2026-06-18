<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/332 -->
# sources/test-tools/xfstests/tests/xfs/332

## Purpose
Make sure query_range returns -EINVAL if lowkey > highkey. In this subset it exercises reverse mapping metadata and owner-accounting validation; reflink, CoW, refcount, and shared-extent behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick rmap clone collapse punch insert zero prealloc`. It imports common/preamble, common/filter, common/attr. Local helpers are no local shell helpers. Requirement and fix gates include `_require_xfs_scratch_rmapbt`; `_require_command "$XFS_DB_PROG" "xfs_db"`; `_require_xfs_io_command "falloc"`; `_require_xfs_io_command "fpunch"`; `_require_xfs_io_command "fzero"`; `_require_xfs_io_command "fcollapse"`; `_require_xfs_io_command "finsert"`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_db`, `mount`, `stat`, `file`, `rm`, `sync`. Key shell state is carried in `blksz`, `blocks`, `len`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 16: `_require_xfs_scratch_rmapbt`; line 17: `_require_command "$XFS_DB_PROG" "xfs_db"`; line 18: `_require_xfs_io_command "falloc"`; line 19: `_require_xfs_io_command "fpunch"`; line 20: `_require_xfs_io_command "fzero"`; line 21: `_require_xfs_io_command "fcollapse"`; line 22: `_require_xfs_io_command "finsert"`; line 24: `rm -f "$seqres.full"`; line 26: `echo "Format and mount"`; plus 3 further source-derived command steps.. compares GETFSMAP/xfs_io fsmap output against expected owners, devices, or bmap records The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include expected-output drift, missing helper binaries, and unsupported scratch geometry are the main hazards. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/332 -->
