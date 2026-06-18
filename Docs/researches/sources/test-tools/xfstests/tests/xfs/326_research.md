<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/326 -->
# sources/test-tools/xfstests/tests/xfs/326

## Purpose
Reflink a file with a few dozen extents, CoW a few blocks, and rm. Inject an error during refcount updates to test log recovery. Use cowextsize so that the refcount failure is somewhere in the CoW remap instead of when we're stashing the CoW orphan record. In this subset it exercises reflink, CoW, refcount, and shared-extent behavior; journal/log geometry or recovery behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick clone punch`. It imports common/preamble, common/filter, common/reflink, common/inject. Local helpers are `_cleanup`. Requirement and fix gates include `_require_cp_reflink`; `_require_scratch_reflink`; `_require_xfs_io_command "cowextsize"`; `_require_xfs_io_command "fpunch"`; `_require_xfs_io_error_injection "refcount_finish_one"`; `_require_congruent_file_oplen $SCRATCH_MNT $blksz`; `_require_no_xfs_always_cow`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `file`, `touch`, `cp`, `rm`, `sync`. Key shell state is carried in `blksz`, `blks`, `sz`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 19: `_scratch_unmount > /dev/null 2>&1`; line 20: `rm -rf $tmp.*`; line 30: `_require_xfs_io_command "cowextsize"`; line 31: `_require_xfs_io_command "fpunch"`; line 32: `_require_xfs_io_error_injection "refcount_finish_one"`; line 37: `echo "Format filesystem"`; line 38: `_scratch_mkfs >/dev/null 2>&1`; line 39: `_scratch_mount >> $seqres.full`; line 42: `$XFS_IO_PROG -c "cowextsize $sz" $SCRATCH_MNT`; plus 3 further source-derived command steps.. error injection knobs: refcount_finish_one creates shared extents and CoW/refcount state The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include shared extent and CoW accounting depends on reflink/refcount support; error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/326 -->
