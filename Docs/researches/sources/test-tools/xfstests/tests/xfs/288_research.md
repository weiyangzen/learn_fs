<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/288 -->
# sources/test-tools/xfstests/tests/xfs/288

## Purpose
When an attribute leaf block count is 0, xfs_repair should junk that leaf directly (as xfsprogs commit f714016). In this subset it exercises xfs_repair detection and correction of crafted metadata damage; metadata fuzzing through common/fuzzy helper paths; extended attribute metadata behavior; directory metadata layout and traversal behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick repair fuzzers attr`. It imports common/preamble, common/filter, common/attr. Local helpers are no local shell helpers. Requirement and fix gates include `_require_scratch`; `_require_attrs`; `_notrun "xfs_db can't set attr hdr.count to 0"`. External tools and command surfaces visible in the source include `xfs_db`, `xfs_repair`, `setfattr`, `mount`, `stat`, `grep`, `sed`, `file`, `touch`, `rm`. Key shell state is carried in `inum`, `maxisize`, `count`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 23: `_xfs_force_no_pptrs`; line 26: `_scratch_mkfs_xfs 2>/dev/null | _filter_mkfs 2>$tmp.mkfs >/dev/null`; line 29: `_scratch_mount`; line 31: `touch $SCRATCH_MNT/$seq.attrfile`; line 39: `$SETFATTR_PROG -n "user.testattr${seq}" \`; line 41: `$SCRATCH_MNT/$seq.attrfile`; line 43: `_scratch_unmount`; line 45: `_scratch_xfs_set_metadata_field "hdr.count" "0" \`; line 50: `count=$(_scratch_xfs_get_metadata_field "hdr.count" \`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; stress/race coverage is timing-sensitive and can expose hangs rather than clean assertion failures. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/288 -->
