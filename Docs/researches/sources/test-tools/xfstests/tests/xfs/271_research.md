<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/271 -->
# sources/test-tools/xfstests/tests/xfs/271

## Purpose
Check that getfsmap reports the AG metadata we're expecting. In this subset it exercises filesystem space-map reporting and consistency with file block maps; reverse mapping metadata and owner-accounting validation. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick rmap fsmap`. It imports common/preamble, common/filter. Local helpers are `_cleanup`. Requirement and fix gates include `_require_xfs_scratch_rmapbt`; `_require_xfs_io_command "fsmap"`; `_require_xfs_has_feature "$SCRATCH_MNT" reflink`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `grep`, `rm`. Key shell state is carried in `agcount`, `agcount_wiggle`, `has_reflink`, `perag_metadata_exts`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 16: `rm -rf "$tmp".* $TEST_DIR/fsmap $TEST_DIR/testout`; line 22: `_require_xfs_scratch_rmapbt`; line 23: `_require_xfs_io_command "fsmap"`; line 25: `rm -f "$seqres.full"`; line 27: `echo "Format and mount"`; line 28: `_scratch_mkfs > "$seqres.full" 2>&1`; line 29: `_scratch_mount`; line 31: `agcount=$(_xfs_mount_agcount $SCRATCH_MNT)`; line 33: `_xfs_has_feature $SCRATCH_MNT rtgroups && agcount_wiggle=1`; plus 3 further source-derived command steps.. compares GETFSMAP/xfs_io fsmap output against expected owners, devices, or bmap records creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/271 -->
