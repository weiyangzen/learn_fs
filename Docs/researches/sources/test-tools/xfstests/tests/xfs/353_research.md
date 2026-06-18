<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/353 -->
# sources/test-tools/xfstests/tests/xfs/353

## Purpose
Populate a XFS filesystem and fuzz every AGF field. Use xfs_scrub to fix the corruption. In this subset it exercises xfs_repair detection and correction of crafted metadata damage; xfs_scrub online checking or repair of populated/fuzzed filesystems; metadata fuzzing through common/fuzzy helper paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest dangerous_fuzzers scrub fuzzers_online_repair`. It imports common/preamble, common/filter, common/populate, common/fuzzy. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch_xfs_fuzz_fields`. External tools and command surfaces visible in the source include `xfs_scrub`, `stat`, `file`, `rm`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `_require_scratch_xfs_fuzz_fields`; line 22: `echo "Format and populate"`; line 23: `_scratch_populate_cached nofill > $seqres.full 2>&1`; line 25: `echo "Fuzz AGF"`; line 26: `_scratch_xfs_fuzz_metadata '' 'online' 'agf 0' >> $seqres.full`; line 27: `echo "Done fuzzing AGF"`. metadata fuzzing target: _scratch_xfs_fuzz_metadata '' 'online' 'agf 0' >> $seqres.full The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/353 -->
