<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/426 -->
# sources/test-tools/xfstests/tests/xfs/426

## Purpose
Populate a XFS filesystem and fuzz every user dquot field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy, common/quota. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`; `_require_quota`. External tools and command surfaces visible in the source include `xfs_scrub`, `mount`, `stat`, `file`, `rm`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 21: `_require_scratch_xfs_fuzz_fields`; line 24: `echo "Format and populate"`; line 25: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 27: `_scratch_mount`; line 28: `$here/src/feature -U $SCRATCH_DEV || _notrun "user quota disabled"`; line 29: `_scratch_unmount`; line 31: `_scratch_xfs_set_quota_fuzz_ids`; line 33: `for id in "${SCRATCH_XFS_QUOTA_FUZZ_IDS[@]}"; do`; line 34: `echo "Fuzz user $id dquot"`; plus 2 further source-derived command steps.. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online'  "dquot -u $id" >> $seqres.full mounts or inspects quota state and dquot accounting The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; quota state can persist through remounts and is sensitive to mount options. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/426 -->
