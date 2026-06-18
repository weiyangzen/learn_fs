<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/291 -->
# sources/test-tools/xfstests/tests/xfs/291

## Purpose
Test xfs_repair on fragmented multi-block dir2 fs In this subset it exercises xfsdump/xfsrestore compatibility and metadata preservation; xfs_metadump/xfs_mdrestore metadata image coverage; xfs_repair detection and correction of crafted metadata damage; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto repair metadump`. It imports common/preamble, common/filter, common/metadump. Local helpers are `_cleanup`. Requirement and fix gates include `_require_command "$XFS_MDRESTORE_PROG" "xfs_mdrestore"`; `_require_scratch`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_db`, `xfs_repair`, `xfs_mdrestore`, `xfs_metadump`, `dd`, `mount`, `stat`, `diff`, `file`, `touch`, `mkdir`. Key shell state is carried in `logblks`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 16: `rm -r -f $tmp.*`; line 17: `_xfs_cleanup_verify_metadump`; line 24: `_require_command "$XFS_MDRESTORE_PROG" "xfs_mdrestore"`; line 25: `_xfs_setup_verify_metadump`; line 28: `logblks=$(_scratch_find_xfs_min_logblocks -n size=16k -d size=133m)`; line 29: `_scratch_mkfs_sized $((133 * 1048576)) '' -n size=16k -l size=${logblks}b >> $seqres.full 2>&1`; line 30: `_scratch_mount`; line 40: `mkdir $SCRATCH_MNT/fragdir`; line 41: `for I in `seq 0 26200`; do`; plus 3 further source-derived command steps.. verifies metadump/mdrestore behavior and image fidelity The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include expected-output drift, missing helper binaries, and unsupported scratch geometry are the main hazards. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/291 -->
