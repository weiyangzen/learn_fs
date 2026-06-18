<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/311 -->
# sources/test-tools/xfstests/tests/xfs/311

## Purpose
Test to reproduce an XFS unmount crash due to races with directory readahead. XFS had a bug in which unmount would proceed with a readahead I/O in flight. If the unmount deconstructed the log by the time I/O completion occurs, certain metadata read verifier checks could access invalid memory and cause a panic. In this subset it exercises mount/remount acceptance and rejection paths; directory metadata layout and traversal behavior; journal/log geometry or recovery behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick`. It imports common/preamble, common/dmdelay. Local helpers are `_cleanup`. Requirement and fix gates include `_require_scratch`; `_require_dm_target delay`. External tools and command surfaces visible in the source include `xfs_io`, `mount`, `stat`, `mkdir`, `rm`, `sync`. Key shell state is carried in mostly transient harness variables, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 20: `rm -f $tmp.*`; line 21: `_scratch_unmount > /dev/null 2>&1`; line 33: `echo "Silence is golden."`; line 35: `_scratch_mkfs_xfs >> $seqres.full 2>&1`; line 42: `mkdir $SCRATCH_MNT/dir`; line 43: `for i in $(seq 0 999); do`; line 44: `echo > $SCRATCH_MNT/dir/$i`; line 59: `$XFS_IO_PROG -c "bmap -v" $SCRATCH_MNT/dir >> $seqres.full 2>&1`. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include stress/race coverage is timing-sensitive and can expose hangs rather than clean assertion failures. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/311 -->
