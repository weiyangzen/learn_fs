# sources/test-tools/xfstests/tests/generic/591

## Purpose

Test using splice() to read from pipes.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick rw pipe splice`. It imports `./common/preamble`. Prerequisite and skip gates include `_require_test`, `_require_odirect`, `_require_test_program "splice-test"`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `min_dio_alignment`, `splice-test`. Important harness variables and paths include `TEST_DIR`, `TEST_DEV`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `_require_odirect`; `_require_test_program "splice-test"`; `diosize=`$here/src/min_dio_alignment $TEST_DIR $TEST_DEV``; `$here/src/splice-test -s $diosize -r $TEST_DIR/a`; `$here/src/splice-test -rd $TEST_DIR/a`; `$here/src/splice-test -s $diosize $TEST_DIR/a`; `$here/src/splice-test -d $TEST_DIR/a`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/591.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
