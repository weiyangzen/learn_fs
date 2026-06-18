<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/279 -->
# sources/test-tools/xfstests/tests/xfs/279

## Purpose
Test mkfs.xfs against various types of devices with varying logical & physical sector sizes and offsets. In this subset it exercises mkfs.xfs formatting and geometry validation; journal/log geometry or recovery behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto mkfs`. It imports common/preamble, common/filter, common/scsi_debug. Local helpers are `_cleanup`, `_wipe_device`, `_check_mkfs`. Requirement and fix gates include `_require_scsi_debug`. External tools and command surfaces visible in the source include `mkfs.xfs`, `dd`, `stat`, `awk`, `sed`, `rm`. Key shell state is carried in `size`, `device`, `SCSI_DEBUG_DEV`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 17: `rm -f $tmp.*`; line 33: `dd if=/dev/zero of=$device bs=4k count=1 &>/dev/null`; line 38: `echo "==================="`; line 39: `echo "mkfs with opts: $@" | sed -e "s,$SCSI_DEBUG_DEV,DEVICE,"`; line 40: `$MKFS_XFS_PROG $@ 2>/dev/null > $tmp.mkfs.full`; line 41: `if [ $? -ne 0 ]; then`; line 42: `echo "Failed."`; line 45: `echo "Passed."`; line 46: `cat $tmp.mkfs.full | _filter_mkfs >> $seqres.full 2>$tmp.mkfs`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include expected-output drift, missing helper binaries, and unsupported scratch geometry are the main hazards. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/279 -->
