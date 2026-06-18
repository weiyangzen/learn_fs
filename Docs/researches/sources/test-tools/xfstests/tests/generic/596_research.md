# sources/test-tools/xfstests/tests/generic/596

## Purpose

Regression test for the bug fixed by commit 10a98cb16d80 ("xfs: clear PF_MEMALLOC before exiting xfsaild thread"). If the bug exists, a kernel WARNING should be triggered. See the commit message for details.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_bsd_process_accounting`, `_require_chattr S`, `_require_test`, `_require_scratch`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `accton`, `chattr`, `seq`, `touch`. Important harness variables and paths include `TEST_DIR`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_bsd_process_accounting`; `_require_chattr S`; `_require_test`; `_require_scratch`; `rm -f $accounting_file`; `touch $accounting_file`; `$CHATTR_PROG +S $accounting_file`; `_scratch_mkfs &>> $seqres.full`; `$ACCTON_PROG $accounting_file >> $seqres.full`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/596.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
