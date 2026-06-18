<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/290 -->
# sources/test-tools/xfstests/tests/xfs/290

## Purpose
Makes calls to XFS_IOC_ZERO_RANGE and checks tossed ranges Nothing should be tossed unless the range includes a page boundry Primarily tests page boundries and boundries that are off-by-one to ensure we're only tossing what's expected In this subset it exercises XFS regression behavior exercised through the xfstests harness. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto rw prealloc quick ioctl zero`. It imports common/preamble, common/filter, common/punch. Local helpers are no local shell helpers. Requirement and fix gates include `_require_test`; `_require_xfs_io_command "zero"`. External tools and command surfaces visible in the source include `xfs_io`, `stat`, `sed`, `file`. Key shell state is carried in `testfile`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 25: `_require_xfs_io_command "zero"`; line 29: `_test_block_boundaries 4096 zero _filter_xfs_io_unique $testfile`. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include expected-output drift, missing helper binaries, and unsupported scratch geometry are the main hazards. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/290 -->
