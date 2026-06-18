# sources/test-tools/xfstests/tests/generic/528

## Purpose

Check that statx btime (aka creation time) is plausibly close to when we created a file. A bug caught during code review of xfs patches revealed that there weren't any sanity checks of the btime values.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick`. It imports `./common/preamble`, `./common/attr`, `./common/filter`. Prerequisite and skip gates include `_require_test`, `_require_xfs_io_command "statx" "-r"`, `_require_btime`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_io`, `seq`, `touch`, `grep`, `stat`. Important harness variables and paths include `TEST_DIR`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `_require_xfs_io_command "statx" "-r"`; `_require_btime`; `rm -f $testfile`; `now=$(date +%s)`; `touch $testfile`; `btime=$(date +%s -d "$($XFS_IO_PROG -c "statx -v -m $STATX_BTIME" $testfile | grep 'stat.btime =' | cut -d '=' -f 2)")`; `test -n "$btime" || echo "error: did not see btime in output??"`; `_within_tolerance "btime" "$btime" "$now" 1 5 -v`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/528.out`; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
