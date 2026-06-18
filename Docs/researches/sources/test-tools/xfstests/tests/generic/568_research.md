# sources/test-tools/xfstests/tests/generic/568

## Purpose

FS QA Test No. generic/568 Test that fallocating an unaligned range allocates all blocks touched by that range

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick rw prealloc`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_xfs_io_command "falloc"`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `xfs_io`, `seq`, `stat`. Important harness variables and paths include `TEST_DIR`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_xfs_io_command "falloc"`; `block_size=$(_get_file_block_size "$TEST_DIR")`; `$XFS_IO_PROG -f -c "falloc $((block_size - 1)) 2" "$testfile"`; `allocated_size_before=$(($(stat -c '%b * %B' "$testfile")))`; `$XFS_IO_PROG -c "pwrite $((block_size - 1)) 2" "$testfile" | _filter_xfs_io | sed -e "s/$((block_size - 1))/block_size - 1/"`; `allocated_size_after=$(($(stat -c '%b * %B' "$testfile")))`; `echo "ERROR: File grew from ${allocated_size_before} B to" "${allocated_size_after} B when writing to the fallocated range."`; `echo "OK: File did not grow."`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/568.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
