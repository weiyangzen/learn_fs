<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/424 -->
# sources/test-tools/xfstests/tests/xfs/424

## Purpose
This case checks if setting type causes error. On crc filesystems, xfs_db doesn't take sector size into account when setting type, and this can result in an errant crc. This issue has been fixed in xfsprogs-dev: '55f224b ("xfs_db: update buffer size when new type is set")' On crc filesystems, when setting the type to "inode" the verifier validates multiple inodes in the current fs block, so setting the buffer size to that of just one inode is not sufficient and it'll emit spurious verifier errors for all but the first. This issue has been fixed in xfsprogs-dev: '533d1d2 ("xfs_db: properly set inode type")' In this subset it exercises XFS regression behavior exercised through the xfstests harness. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick db`. It imports common/preamble, common/filter. Local helpers are `filter_dbval`. Requirement and fix gates include `_require_scratch_nocheck`. External tools and command surfaces visible in the source include `xfs_db`, `mkfs.xfs`, `dd`, `stat`, `grep`, `awk`, `diff`, `file`, `blockdev`. Key shell state is carried in `sec_sz`, `sector_sizes`, `finobt_enabled`, `DADDR`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 34: `echo "Silence is golden."`; line 48: `while [ $sec_sz -le 4096 ]; do`; line 53: `for SECTOR_SIZE in $sector_sizes; do`; line 55: `$MKFS_XFS_PROG -f -s size=$SECTOR_SIZE $SCRATCH_DEV | \`; line 56: `grep -q 'finobt=1' && finobt_enabled=1`; line 58: `for TYPE in agf agi agfl sb; do`; line 61: `$XFS_DB_PROG -c "daddr $DADDR" -c "type $TYPE" $SCRATCH_DEV`; line 66: `$XFS_DB_PROG -c "daddr $DADDR" -c "type inode" $SCRATCH_DEV`; line 69: `$XFS_DB_PROG -c "daddr $DADDR" -c "type bnobt" $SCRATCH_DEV`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/424 -->
