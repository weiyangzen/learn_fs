<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/328 -->
# sources/test-tools/xfstests/tests/xfs/328

## Purpose
See how well xfs_fsr handles "defragging" a file with a hojillion extents. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; xfs_fsr defragmentation and exchangerange recovery. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone fsr prealloc`. It imports common/preamble, common/filter, common/attr, common/reflink. Local helpers are `calc_space`. Requirement and fix gates include `_require_scratch_reflink`; `_require_cp_reflink`; `_require_test_program "punch-alternating"`; `_require_xfs_io_command "falloc" # used in FSR`; `_require_command "$XFS_FSR_PROG" "xfs_fsr"`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_fsr`, `mount`, `stat`, `sed`, `file`, `mkdir`, `cp`, `rm`, `punch-alternating`. Key shell state is carried in `testdir`, `fnr`, `free_blocks`, `blksz`, `space_avail`, `blocks_needed`, `space_needed`, `bytes`, `old_nextents`, `new_nextents`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_xfs_io_command "falloc" # used in FSR`; line 21: `_require_command "$XFS_FSR_PROG" "xfs_fsr"`; line 23: `rm -f "$seqres.full"`; line 25: `echo "Format and mount"`; line 26: `_scratch_mkfs > "$seqres.full" 2>&1`; line 27: `_scratch_mount >> "$seqres.full" 2>&1`; line 30: `mkdir "$testdir"`; line 44: `while test $space_needed -gt $space_avail; do`; line 51: `echo "Create a many-block file"`; plus 3 further source-derived command steps.. drives xfs_fsr defragmentation paths creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/328 -->
