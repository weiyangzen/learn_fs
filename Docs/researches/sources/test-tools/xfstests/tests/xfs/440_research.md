<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/440 -->
# sources/test-tools/xfstests/tests/xfs/440

## Purpose
Regression test for a quota accounting bug when changing the owner of a file that has CoW reservations and no dirty pages. The reservations should shift over to the new owner, but they do not. unreliable_in_parallel: external sync(1) and/or drop caches can reclaim inodes and free post-eof space, resulting in lower than expected block counts. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; quota accounting, dquot metadata, and quota mount mode handling; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone quota unreliable_in_parallel`. It imports common/preamble, common/reflink, common/quota, common/filter. Local helpers are no local shell helpers. Requirement and fix gates include `_require_quota`; `_require_scratch_delalloc`; `_require_scratch_reflink`; `_require_cp_reflink`; `_require_user`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `grep`, `file`, `touch`, `cp`, `rm`, `chown`, `sync`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 31: `echo "Format and mount"`; line 32: `_scratch_mkfs > "$seqres.full" 2>&1`; line 33: `_scratch_mount "-o usrquota,grpquota" >> "$seqres.full" 2>&1`; line 36: `_xfs_force_bdev data $SCRATCH_MNT`; line 38: `echo "Create files"`; line 39: `$XFS_IO_PROG -c "cowextsize 1m" $SCRATCH_MNT`; line 40: `touch $SCRATCH_MNT/a $SCRATCH_MNT/force_fsgqa`; line 41: `chown $qa_user $SCRATCH_MNT/a $SCRATCH_MNT/force_fsgqa`; line 42: `_pwrite_byte 0x58 0 64k $SCRATCH_MNT/a >> $seqres.full`; plus 3 further source-derived command steps.. mounts or inspects quota state and dquot accounting creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include quota state can persist through remounts and is sensitive to mount options; shared extent and CoW accounting depends on reflink/refcount support. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/440 -->
