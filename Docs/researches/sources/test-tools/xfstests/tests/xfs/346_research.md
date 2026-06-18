<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/346 -->
# sources/test-tools/xfstests/tests/xfs/346

## Purpose
Test fragmentation after writing and dropping CoW extent hint reservation: - Create two reflinked files. Set extsz hint on second file. - Directio write to random offsets to scatter CoW reservations. - Unmount, remount, repeat (twice more). - Check the number of extents. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; mount/remount acceptance and rejection paths; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone fiemap unshare`. It imports common/preamble, common/filter, common/reflink. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_reflink`; `_require_cp_reflink`; `_require_xfs_io_command "fiemap"`; `_require_xfs_io_command "cowextsize"`; `_require_xfs_io_command "funshare"`; `_require_odirect`; `_require_congruent_file_oplen $SCRATCH_MNT $blksz`; `_require_fs_space $SCRATCH_MNT $((filesize / 1024 * 3 * 5 / 4))`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `file`, `mkdir`, `cp`, `rm`. Key shell state is carried in `testdir`, `blksz`, `nr`, `filesize`, `bufnr`, `bufsize`, `real_blksz`, `internal_blks`, `old_extents`, `new_extents`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 22: `_require_xfs_io_command "fiemap"`; line 23: `_require_xfs_io_command "cowextsize"`; line 24: `_require_xfs_io_command "funshare"`; line 27: `echo "Format and mount"`; line 28: `_scratch_mkfs > $seqres.full 2>&1`; line 29: `_scratch_mount >> $seqres.full 2>&1`; line 32: `mkdir $testdir`; line 45: `echo "Create the original files"`; line 46: `$XFS_IO_PROG -f -c "pwrite -S 0x61 -b $bufsize 0 $((filesize + 1))" $testdir/file1 >> $seqres.full`; plus 3 further source-derived command steps.. creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/346 -->
