<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/306 -->
# sources/test-tools/xfstests/tests/xfs/306

## Purpose
Regression test for an XFS multi-block buffer logging bug. The XFS bug results in a panic when a non-contiguous multi-block buffer is mapped and logged in a particular manner, such that only regions beyond the first fsb-sized mapping are logged. The crash occurs asynchronous to transaction submission, when the associated buffer log item is pushed from the CIL (i.e., when the log is subsequently flushed). In this subset it exercises journal/log geometry or recovery behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick punch`. It imports common/preamble. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_nocheck	# check complains about single AG fs`; `_require_xfs_io_command "fpunch"`; `_require_command $UUIDGEN_PROG uuidgen`; `_require_test_program "punch-alternating"`; `_require_xfs_scratch_non_zoned`. External tools and command surfaces visible in the source include `xfs_io`, `dd`, `mount`, `stat`, `file`, `touch`, `mkdir`, `ln`, `sync`, `punch-alternating`. Key shell state is carried in `i`, `f`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 23: `_require_xfs_io_command "fpunch"`; line 33: `_scratch_mkfs_xfs -d size=100m -n size=64k >> $seqres.full 2>&1`; line 34: `_scratch_mount`; line 38: `_require_xfs_scratch_non_zoned`; line 42: `mkdir $SCRATCH_MNT/src`; line 43: `for i in $(seq 0 1023); do`; line 44: `touch $SCRATCH_MNT/src/`$UUIDGEN_PROG``; line 48: `for i in $(seq 0 3); do`; line 49: `mkdir $SCRATCH_MNT/$i`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/306 -->
