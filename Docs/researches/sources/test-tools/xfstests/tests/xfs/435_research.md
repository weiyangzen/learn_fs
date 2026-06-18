<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/435 -->
# sources/test-tools/xfstests/tests/xfs/435

## Purpose
Ensure that we don't leak dquots when CoW recovery fails. Corrupt the refcount btree to ensure that the CoW garbage collection (and therefore the mount) fail. On a subsequent mount attempt, we should be able to release the quota inodes when we're aborting the mount. We also should not leak dquots. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; quota accounting, dquot metadata, and quota mount mode handling; mount/remount acceptance and rejection paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone`. It imports common/preamble, common/filter, common/attr, common/reflink, common/quota, common/module. Local helpers are no local shell helpers. Requirement and fix gates include `_require_quota`; `_require_scratch_reflink`; `_require_cp_reflink`; `_disable_dmesg_check`; `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. External tools and command surfaces visible in the source include `xfs_db`, `dd`, `mount`, `stat`, `file`, `mkdir`, `cp`, `rm`. Key shell state is carried in `testdir`, `blksz`, `blks`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 30: `rm -f "$seqres.full"`; line 32: `echo "Format and mount"`; line 33: `_scratch_mkfs > "$seqres.full" 2>&1`; line 34: `_scratch_mount -o quota >> "$seqres.full" 2>&1`; line 40: `mkdir "$testdir"`; line 42: `echo "Create a many-block file"`; line 43: `_pwrite_byte 0x62 0 $((blksz * blks)) $testdir/file1 >> $seqres.full`; line 44: `_pwrite_byte 0x63 0 $blksz $testdir/file2 >> $seqres.full`; line 45: `_reflink_range $testdir/file2 0 $testdir/file1 $blksz $blksz >> $seqres.full`; plus 3 further source-derived command steps.. mounts or inspects quota state and dquot accounting creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; quota state can persist through remounts and is sensitive to mount options; shared extent and CoW accounting depends on reflink/refcount support. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/435 -->
