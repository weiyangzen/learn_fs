<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/294 -->
# sources/test-tools/xfstests/tests/xfs/294

## Purpose
Test readdir on fragmented multi-fsb dir blocks If the readahead map ends with a partial multi-fsb dir block, the loop at the end of xfs_dir2_leaf_readbuf() may walk off the end of the mapping array, read garbage, corrupt the loop control counter, and never return. Failure is a hang; KASAN should also catch this. In this subset it exercises directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto dir metadata prealloc punch`. It imports common/preamble, common/filter. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch`; `_require_test_program "punch-alternating"`; `_require_xfs_io_command "falloc"`; `_require_xfs_io_command "fpunch"`. External tools and command surfaces visible in the source include `xfs_io`, `dd`, `mount`, `stat`, `file`, `touch`, `mkdir`, `rm`, `sync`, `punch-alternating`. Key shell state is carried in `MKFS_OPTIONS`, `space`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 26: `_require_xfs_io_command "falloc"`; line 27: `_require_xfs_io_command "fpunch"`; line 31: `_scratch_mkfs "-d size=512m -n size=8192 -i size=1024" >> $seqres.full 2>&1 \`; line 33: `_scratch_mount`; line 37: `mkdir $SCRATCH_MNT/tmp`; line 38: `for I in `seq 1 10000`; do touch $SCRATCH_MNT/tmp/$I; done`; line 41: `mkdir $SCRATCH_MNT/clusters`; line 42: `for I in `seq 1 32 10000`; do`; line 45: `rm -rf $SCRATCH_MNT/tmp`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/294 -->
