# sources/test-tools/xfstests/tests/generic/595

## Purpose

Regression test for a bug in the FS_IOC_REMOVE_ENCRYPTION_KEY ioctl fixed by commit 2b4eae95c736 ("fscrypt: don't evict dirty inodes after removing key"). This bug could cause writes to encrypted files to be lost if they raced with the corresponding fscrypt master key being removed. With f2fs, this bug could also crash the kernel.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick encrypt`. It imports `./common/preamble`, `./common/filter`, `./common/encrypt`. Prerequisite and skip gates include `_require_scratch_encryption -v 2`, `_require_command "$KEYCTL_PROG" keyctl`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `keyctl`, `touch`, `wait`, `mkdir`, `sleep`, `stat`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`, `TIME_FACTOR`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_encryption -v 2`; `_require_command "$KEYCTL_PROG" keyctl`; `_scratch_mkfs_encrypted &>> $seqres.full`; `_scratch_mount`; `runtime=$((4 * TIME_FACTOR))`; `mkdir $dir`; `_set_encpolicy $dir $TEST_KEY_IDENTIFIER`; `_add_enckey $SCRATCH_MNT "$TEST_RAW_KEY"`; `echo -e "\n# Single-threaded reproducer"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; creates encrypted directories/files and manipulates fscrypt keys or nonce/ciphertext metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

fscrypt policy/key support and raw metadata inspection differ across filesystems and kernel versions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/595.out`; content dumps/hexdumps expose corruption or unexpected nonzero data. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
