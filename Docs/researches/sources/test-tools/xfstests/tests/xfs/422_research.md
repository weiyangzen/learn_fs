<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/422 -->
# sources/test-tools/xfstests/tests/xfs/422

## Purpose
Race fsstress and rmapbt repair for a while to see if we crash or livelock. In this subset it exercises reverse mapping metadata and owner-accounting validation; xfs_repair detection and correction of crafted metadata damage; filesystem freeze/unfreeze behavior under stress or error injection. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest online_repair fsstress_online_repair freeze`. It imports common/preamble, common/filter, common/fuzzy, common/inject. Local helpers are `_cleanup`. Requirement and fix gates include `_require_scratch`; `_require_xfs_stress_online_repair`; `_require_xfs_has_feature "$SCRATCH_MNT" rmapbt`. External tools and command surfaces visible in the source include `fsstress`, `mount`, `stat`, `rm`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 13: `_scratch_xfs_stress_scrub_cleanup &> /dev/null`; line 15: `rm -r -f $tmp.*`; line 25: `_require_xfs_stress_online_repair`; line 27: `_scratch_mkfs > "$seqres.full" 2>&1`; line 28: `_scratch_mount`; line 29: `_require_xfs_has_feature "$SCRATCH_MNT" rmapbt`; line 30: `_scratch_xfs_stress_online_repair -s "repair rmapbt %agno%"`; line 33: `echo Silence is golden`. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; error-injection timing and shutdown/recovery behavior are kernel-sensitive; stress/race coverage is timing-sensitive and can expose hangs rather than clean assertion failures. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/422 -->
