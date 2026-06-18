<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/298 -->
# sources/test-tools/xfstests/tests/xfs/298

## Purpose
Test that inline symlinks are removed from the inode when an extended attributes forces it into being remote symlink. Warning: this test will ASSERT on unpatched DEBUG XFS. In this subset it exercises extended attribute metadata behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto attr symlink quick`. It imports common/preamble, common/filter. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch`. External tools and command surfaces visible in the source include `xfs_db`, `dd`, `mount`, `umount`, `stat`, `awk`, `ln`, `rm`. Key shell state is carried in `SYMLINK_FILE`, `SYMLINK`, `SYMLINK_ADD`, `SIZE`, `inode`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 23: `_scratch_mkfs_xfs >/dev/null 2>&1`; line 32: `while [ $SIZE -lt 1024 ];do`; line 33: `_scratch_mount >/dev/null 2>&1`; line 35: `echo "Testing symlink size $SIZE"`; line 37: `ln -s $SYMLINK $SYMLINK_FILE > /dev/null 2>&1`; line 49: `rm $SYMLINK_FILE`; line 52: `_scratch_unmount >/dev/null 2>&1`; line 53: `_scratch_xfs_db  -c "inode $inode" -c "p core.nextents"`. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include expected-output drift, missing helper binaries, and unsupported scratch geometry are the main hazards. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/298 -->
