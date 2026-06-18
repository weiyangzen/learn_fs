<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/343 -->
# sources/test-tools/xfstests/tests/xfs/343

## Purpose
Basic rmap manipulation tests for realtime files. In this subset it exercises reverse mapping metadata and owner-accounting validation; realtime device allocation and realtime reverse-map behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick rmap collapse punch insert zero realtime prealloc`. It imports common/preamble, common/filter. Local helpers are no local shell helpers. Requirement and fix gates include `_require_realtime`; `_require_xfs_scratch_rmapbt`; `_require_xfs_io_command "falloc"`; `_require_xfs_io_command "fpunch"`; `_require_xfs_io_command "fzero"`; `_require_xfs_io_command "fcollapse"`; `_require_xfs_io_command "finsert"`; `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `file`, `rm`, `sync`. Key shell state is carried in `blksz`, `blocks`, `len`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 16: `_require_xfs_scratch_rmapbt`; line 17: `_require_xfs_io_command "falloc"`; line 18: `_require_xfs_io_command "fpunch"`; line 19: `_require_xfs_io_command "fzero"`; line 20: `_require_xfs_io_command "fcollapse"`; line 21: `_require_xfs_io_command "finsert"`; line 23: `rm -f "$seqres.full"`; line 25: `echo "Format and mount"`; line 26: `_scratch_mkfs > "$seqres.full" 2>&1`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include realtime device geometry and internal/external rt-device handling affect expected output. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/343 -->
