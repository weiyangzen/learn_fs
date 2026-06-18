<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/302 -->
# sources/test-tools/xfstests/tests/xfs/302

## Purpose
Dump and restore partialmax + 1 wholly-sparse files In this subset it exercises xfsdump/xfsrestore compatibility and metadata preservation. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto dump`. It imports common/preamble, common/filter, common/dump. Local helpers are `_cleanup`. Requirement and fix gates include `_require_scratch`. External tools and command surfaces visible in the source include `xfs_io`, `xfsdump`, `xfsrestore`, `mount`, `stat`, `file`, `mkdir`, `rm`, `truncate`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 17: `rm -f $tmp.*`; line 27: `_scratch_mkfs_xfs >>$seqres.full`; line 28: `_scratch_mount`; line 30: `echo "Silence is golden."`; line 31: `mkdir $dump_dir >> $seqres.full 2>&1 || _fail "mkdir \"$dump_dir\" failed"`; line 32: `for i in `seq 1 4`; do`; line 33: `$XFS_IO_PROG -f -c "truncate 1t" $dump_dir/sparsefile$i \`; line 38: `$XFSDUMP_PROG -L session -M label1 -M label2 -f $tmp.stream1 \`; line 41: `$XFSRESTORE_PROG -F -f $tmp.stream1 -f $tmp.stream2 $restore_dir \`. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include expected-output drift, missing helper binaries, and unsupported scratch geometry are the main hazards. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/302 -->
