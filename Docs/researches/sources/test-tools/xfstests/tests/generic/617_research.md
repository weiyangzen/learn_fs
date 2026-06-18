# sources/test-tools/xfstests/tests/generic/617

## Purpose

IO_URING soak direct-IO fsx test, copy from generic/521 but reduce the number fsx ops to limit the testing time to be an auto group test.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto rw io_uring stress soak`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_test`, `_require_odirect`, `_require_io_uring`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `feature`, `seq`. Important harness variables and paths include `TEST_DIR`, `seq`, `TIME_FACTOR`, `LOAD_FACTOR`, `SOAK_DURATION`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `_require_odirect`; `_require_io_uring`; `nr_ops=$((20000 * TIME_FACTOR))`; `op_sz=$((128000 * LOAD_FACTOR))`; `min_dio_sz=$($here/src/feature -s)`; `fsx_args=(-S 0)`; `fsx_args+=(-U)`; `fsx_args+=(-q)`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/617.out`; success is mostly silence after prerequisite and operation checks; fsx/fsstress style stress exits cleanly and emits only filtered diagnostics. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
