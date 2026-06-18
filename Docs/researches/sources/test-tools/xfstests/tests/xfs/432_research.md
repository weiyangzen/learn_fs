<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/432 -->
# sources/test-tools/xfstests/tests/xfs/432

## Purpose
Ensure that metadump copies large directory extents Metadump helpfully discards directory (and xattr) extents that are longer than 1000 blocks. This is a little silly since a hardlink farm can easily create such a monster. Now that we've upped metadump's default too-long-extent discard threshold to 2^21 blocks, make sure we never do that again. In this subset it exercises xfsdump/xfsrestore compatibility and metadata preservation; xfs_metadump/xfs_mdrestore metadata image coverage; extended attribute metadata behavior; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick dir metadata metadump`. It imports common/preamble, common/filter, common/metadump. Local helpers are `_cleanup`, `check_for_long_extent`. Requirement and fix gates include `_require_command "$XFS_MDRESTORE_PROG" "xfs_mdrestore"`; `_require_scratch`. External tools and command surfaces visible in the source include `xfs_db`, `xfs_mdrestore`, `mount`, `stat`, `awk`, `sed`, `file`, `touch`, `mkdir`, `ln`, `rm`. Key shell state is carried in `testdir`, `max_fname_len`, `blksz`, `blocks`, `names`, `name`, `dir_inum`, `inum`, `extlen`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 23: `rm -f "$tmp".*`; line 24: `_xfs_cleanup_verify_metadump`; line 31: `_require_command "$XFS_MDRESTORE_PROG" "xfs_mdrestore"`; line 33: `_xfs_setup_verify_metadump`; line 35: `rm -f "$seqres.full"`; line 37: `echo "Format and mount"`; line 55: `_scratch_mkfs_xfs -b size=1k -n size=64k > "$seqres.full" 2>&1`; line 56: `_scratch_mount >> "$seqres.full" 2>&1`; line 65: `echo "Create huge dir"`; plus 3 further source-derived command steps.. verifies metadump/mdrestore behavior and image fidelity The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include expected-output drift, missing helper binaries, and unsupported scratch geometry are the main hazards. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/432 -->
