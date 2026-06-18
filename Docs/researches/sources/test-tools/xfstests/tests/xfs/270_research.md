<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/270 -->
# sources/test-tools/xfstests/tests/xfs/270

## Purpose
Today ro-compat features can't be mounted rw, but a bug allows an ro->rw remount transition. This bug has been fixed on linux kernel (d0a58e8 xfs: disallow rw remount on fs with unknown ro-compat features), and this case is the regression testcase. In this subset it exercises mount/remount acceptance and rejection paths. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick mount`. It imports common/preamble, common/filter. Local helpers are `set_bad_rocompat`. Requirement and fix gates include `_fixed_by_kernel_commit 74ad4693b647`; `_require_scratch_nocheck`; `_require_scratch_xfs_crc`; `_require_scratch_shutdown`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_db`, `fsstress`, `mount`, `stat`, `grep`, `awk`, `file`. Key shell state is carried in `ro_compat`, `new_ro_compat`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 23: `_require_scratch_xfs_crc`; line 30: `ro_compat=$(_scratch_xfs_get_metadata_field "features_ro_compat" "sb 0")`; line 31: `echo $ro_compat | grep -q -E '^0x[[:xdigit:]]+$'`; line 32: `if [[ $? != 0  ]]; then`; line 33: `echo ":$ro_compat:"`; line 34: `echo "features_ro_compat has an invalid value."`; line 44: `_scratch_xfs_set_metadata_field "features_ro_compat" "$ro_compat" "sb 0" \`; line 48: `new_ro_compat=$(_scratch_xfs_get_metadata_field "features_ro_compat" "sb 0" \`; line 54: `if [ "$new_ro_compat" != "$ro_compat" ]; then`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; stress/race coverage is timing-sensitive and can expose hangs rather than clean assertion failures. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/270 -->
