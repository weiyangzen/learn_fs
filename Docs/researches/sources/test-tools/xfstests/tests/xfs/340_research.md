<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/340 -->
# sources/test-tools/xfstests/tests/xfs/340

## Purpose
Set rrmapino to another inode on an rtrmap fs and see if repair fixes it. In this subset it exercises reverse mapping metadata and owner-accounting validation; realtime device allocation and realtime reverse-map behavior; xfs_repair detection and correction of crafted metadata damage. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick rmap realtime repair`. It imports common/preamble, common/filter. Local helpers are no local shell helpers. Requirement and fix gates include `_require_realtime`; `_require_xfs_scratch_rmapbt`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_db`, `dd`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in `ino`, `rtrmap_accessors`, `rtrmap_path_len`, `rtrmap_entry`, `rrmapino`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 16: `_require_xfs_scratch_rmapbt`; line 18: `rm -f "$seqres.full"`; line 20: `echo "Format and mount"`; line 21: `_scratch_mkfs > "$seqres.full" 2>&1`; line 22: `_scratch_mount`; line 24: `echo "Create some files"`; line 25: `$XFS_IO_PROG -f -R -c "pwrite -S 0x68 0 9999" $SCRATCH_MNT/f1 >> $seqres.full`; line 26: `$XFS_IO_PROG -f -R -c "pwrite -S 0x68 0 9999" $SCRATCH_MNT/f2 >> $seqres.full`; line 27: `echo garbage > $SCRATCH_MNT/f3`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; realtime device geometry and internal/external rt-device handling affect expected output. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/340 -->
