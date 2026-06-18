<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/329 -->
# sources/test-tools/xfstests/tests/xfs/329

## Purpose
Ensure that xfs_fsr handles errors correctly while defragging files. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; xfs_fsr defragmentation and exchangerange recovery. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone fsr`. It imports common/preamble, common/filter, common/attr, common/reflink, common/inject. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_reflink`; `_require_cp_reflink`; `_require_command "$XFS_FSR_PROG" "xfs_fsr"`; `_require_xfs_io_error_injection "bmap_finish_one"`; `_require_xfs_scratch_rmapbt`; `_require_xfs_io_command falloc	# fsr requires support for preallocation`; `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_fsr`, `mount`, `stat`, `file`, `touch`, `mkdir`, `cp`, `rm`. Key shell state is carried in `testdir`, `blksz`, `blks`, `old_nextents`, `new_nextents`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_command "$XFS_FSR_PROG" "xfs_fsr"`; line 21: `_require_xfs_io_error_injection "bmap_finish_one"`; line 22: `_require_xfs_scratch_rmapbt`; line 23: `_require_xfs_io_command falloc	# fsr requires support for preallocation`; line 25: `rm -f "$seqres.full"`; line 27: `echo "Format and mount"`; line 28: `_scratch_mkfs > "$seqres.full" 2>&1`; line 29: `_scratch_mount >> "$seqres.full" 2>&1`; line 35: `mkdir "$testdir"`; plus 3 further source-derived command steps.. error injection knobs: bmap_finish_one drives xfs_fsr defragmentation paths creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support; error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/329 -->
