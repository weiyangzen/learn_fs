<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/341 -->
# sources/test-tools/xfstests/tests/xfs/341

## Purpose
Cross-link file block into rtrmapbt and see if repair fixes it. In this subset it exercises reverse mapping metadata and owner-accounting validation; realtime device allocation and realtime reverse-map behavior; xfs_repair detection and correction of crafted metadata damage. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick rmap realtime prealloc repair`. It imports common/preamble, common/filter. Local helpers are no local shell helpers. Requirement and fix gates include `_require_realtime`; `_require_xfs_scratch_rmapbt`; `_require_test_program "punch-alternating"`; `_disable_dmesg_check`; `_require_xfs_io_command "falloc"`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_db`, `mount`, `stat`, `grep`, `sed`, `file`, `rm`, `punch-alternating`. Key shell state is carried in `blksz`, `rtextsz_blks`, `i_core_size`, `i_ptrs`, `bt_recs`, `blocks`, `len`, `ino`, `fsbno`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 16: `_require_xfs_scratch_rmapbt`; line 19: `_require_xfs_io_command "falloc"`; line 21: `rm -f "$seqres.full"`; line 23: `echo "Format and mount"`; line 24: `_scratch_mkfs | _filter_mkfs 2>$tmp.mkfs >/dev/null`; line 26: `cat $tmp.mkfs > "$seqres.full" 2>&1`; line 27: `_scratch_mount`; line 34: `i_core_size="$(_xfs_get_inode_core_bytes $SCRATCH_MNT)"`; line 41: `echo "Create some files"`; plus 3 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include intentional metadata corruption can make normal post-test fsck inappropriate; realtime device geometry and internal/external rt-device handling affect expected output. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/341 -->
