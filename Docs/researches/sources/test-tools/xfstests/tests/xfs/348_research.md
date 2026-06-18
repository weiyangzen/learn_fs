<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/348 -->
# sources/test-tools/xfstests/tests/xfs/348

## Purpose
FSQA Test No. 348 Test handling of invalid inode modes Set all possible file type values for different types of files and verify that xfs_repair detects the correct errors. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick fuzzers repair`. It imports common/preamble, common/filter, common/repair. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch`; `_disable_dmesg_check`. External tools and command surfaces visible in the source include `xfs_db`, `xfs_repair`, `mount`, `stat`, `grep`, `awk`, `sed`, `diff`, `file`, `touch`, `mkdir`, `ln`. Key shell state is carried in `testdir`, `inode_filter`, `pino`, `inodes`, `ino`, `dtypes`, `ftype`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 32: `_scratch_mkfs >>$seqres.full 2>&1`; line 34: `_scratch_mount`; line 38: `mkdir -p $testdir`; line 39: `mkdir $testdir/DIR`; line 40: `echo 123 > $testdir/DATA`; line 41: `touch $testdir/EMPTY`; line 42: `ln -s $testdir/DATA $testdir/SYMLINK`; line 47: `_xfs_has_feature $SCRATCH_MNT ftype && FTYPE_FEATURE=1`; line 51: `rm -f $inode_filter`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/348 -->
