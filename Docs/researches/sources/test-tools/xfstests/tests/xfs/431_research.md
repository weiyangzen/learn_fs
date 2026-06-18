<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/431 -->
# sources/test-tools/xfstests/tests/xfs/431

## Purpose
Verify kernel doesn't panic when user attempts to set realtime flags on non-realtime FS, using kernel compiled with CONFIG_XFS_RT. Unpatched kernels will panic during this test. Kernels not compiled with CONFIG_XFS_RT should pass test. See CVE-2017-14340 for more information. In this subset it exercises realtime device allocation and realtime reverse-map behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick`. It imports common/preamble, common/filter. Local helpers are no local shell helpers. Requirement and fix gates include `_require_xfs_io_command "chattr" "t"`; `_require_xfs_io_command "fsync"`; `_require_xfs_io_command "pwrite"`; `_require_scratch`. External tools and command surfaces visible in the source include `xfs_io`, `xfs_repair`, `mount`, `stat`, `grep`, `file`, `rm`, `sync`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 22: `_require_xfs_io_command "chattr" "t"`; line 23: `_require_xfs_io_command "fsync"`; line 24: `_require_xfs_io_command "pwrite"`; line 27: `_scratch_mkfs >/dev/null 2>&1`; line 28: `_scratch_mount`; line 32: `_xfs_force_bdev realtime $SCRATCH_MNT &> /dev/null`; line 37: `if $XFS_IO_PROG -c 'lsattr' $SCRATCH_MNT | grep -q 't'; then`; line 39: `$XFS_IO_PROG -fc 'pwrite 0 1m' -c fsync $SCRATCH_MNT/testfile |`; line 40: `tee -a $seqres.full | _filter_xfs_io`; plus 2 further source-derived command steps.. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include realtime device geometry and internal/external rt-device handling affect expected output; error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/431 -->
