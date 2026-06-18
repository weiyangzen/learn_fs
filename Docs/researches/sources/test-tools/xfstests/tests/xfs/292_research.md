<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/292 -->
# sources/test-tools/xfstests/tests/xfs/292

## Purpose
Ensure mkfs with stripe geometry goes into multidisk mode which results in more AGs In this subset it exercises mkfs.xfs formatting and geometry validation. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto mkfs quick`. It imports common/preamble, common/filter. Local helpers are no local shell helpers. Requirement and fix gates include `_require_test`. External tools and command surfaces visible in the source include `xfs_io`, `mkfs.xfs`, `dd`, `stat`, `grep`, `sed`, `file`, `rm`, `truncate`. Key shell state is carried in `fsfile`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 22: `rm -f $fsfile`; line 23: `$XFS_IO_PROG -f -c "truncate 256g" $fsfile`; line 25: `echo "mkfs.xfs without geometry"`; line 26: `mkfs.xfs -f $fsfile | _filter_mkfs 2> $tmp.mkfs > /dev/null`; line 27: `grep -E 'ddev|agcount|agsize' $tmp.mkfs | \`; line 30: `echo "mkfs.xfs with cmdline geometry"`; line 31: `mkfs.xfs -f -d su=16k,sw=5 $fsfile | _filter_mkfs 2> $tmp.mkfs > /dev/null`; line 32: `grep -E 'ddev|agcount|agsize' $tmp.mkfs | \`; line 35: `rm -f $fsfile`. The main integration signal is the scripted xfstests workflow and its golden-output comparison. The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include expected-output drift, missing helper binaries, and unsupported scratch geometry are the main hazards. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/292 -->
