<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/310 -->
# sources/test-tools/xfstests/tests/xfs/310

## Purpose
Create a file with more than 2^21 blocks (the max length of a bmbt record). In this subset it exercises reverse mapping metadata and owner-accounting validation; reflink, CoW, refcount, and shared-extent behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto clone rmap prealloc`. It imports common/preamble, common/filter, common/dmhugedisk. Local helpers are `_cleanup`. Requirement and fix gates include `_require_xfs_scratch_rmapbt`; `_require_scratch_nocheck`; `_require_xfs_io_command "falloc"`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_db`, `xfs_repair`, `dd`, `mount`, `umount`, `stat`, `grep`, `file`, `mkdir`, `rm`. Key shell state is carried in `testdir`, `blksz`, `nr_blks`, `sectors`, `inum`, `nr_bmaps`, `nr_rmaps`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 16: `umount $SCRATCH_MNT > /dev/null 2>&1`; line 18: `rm -rf $tmp.*`; line 25: `_require_xfs_scratch_rmapbt`; line 27: `_require_xfs_io_command "falloc"`; line 30: `echo "Figure out block size"`; line 31: `_scratch_mkfs >/dev/null 2>&1`; line 32: `_scratch_mount >> $seqres.full`; line 37: `_scratch_unmount`; line 39: `echo "Format huge device"`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/310 -->
