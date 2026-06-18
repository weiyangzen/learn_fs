<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/423 -->
# sources/test-tools/xfstests/tests/xfs/423

## Purpose
Race scrubbing the inode record while appending to a file. This exposes a bug in xfs_bmap_count_blocks where we count delalloc extents for di_nblocks if the fork is in extents format, but we don't count them if the fork is in btree format. In this subset it exercises xfs_scrub online checking or repair of populated/fuzzed filesystems. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest scrub prealloc`. It imports common/preamble, common/filter, common/fuzzy, common/inject. Local helpers are no local shell helpers. Requirement and fix gates include `_require_test_program "punch-alternating"`; `_require_xfs_io_command "scrub"`; `_require_xfs_io_command "falloc"`; `_require_scratch`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `diff`, `file`, `rm`, `sync`, `punch-alternating`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 23: `_require_xfs_io_command "scrub"`; line 24: `_require_xfs_io_command "falloc"`; line 27: `echo "Format and populate"`; line 28: `_scratch_mkfs > "$seqres.full" 2>&1`; line 29: `_scratch_mount`; line 31: `$XFS_IO_PROG -f -c 'falloc 0 10m' $SCRATCH_MNT/a >> $seqres.full`; line 32: `$XFS_IO_PROG -f -c 'falloc 0 10m' $SCRATCH_MNT/b >> $seqres.full`; line 33: `$here/src/punch-alternating $SCRATCH_MNT/b`; line 34: `_scratch_sync`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; error-injection timing and shutdown/recovery behavior are kernel-sensitive; stress/race coverage is timing-sensitive and can expose hangs rather than clean assertion failures. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/423 -->
