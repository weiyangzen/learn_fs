# sources/test-tools/xfstests/tests/generic/578

## Purpose

Make sure that we can handle multiple mmap writers to the same file.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick rw clone fiemap mmap`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`. Prerequisite and skip gates include `_require_test_program "mmap-write-concurrent"`, `_require_command "$FILEFRAG_PROG" filefrag`, `_require_xfs_io_command "fiemap"`, `_require_test_reflink`, `_require_cp_reflink`, `_require_congruent_file_oplen $TEST_DIR $blksz`. Local helper functions: `_cleanup`, `compare`. External command surfaces and helper binaries visible in the source include `filefrag`, `mmap-write-concurrent`, `seq`, `od`, `mkdir`, `grep`. Important harness variables and paths include `TEST_DIR`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test_program "mmap-write-concurrent"`; `_require_command "$FILEFRAG_PROG" filefrag`; `_require_xfs_io_command "fiemap"`; `_require_test_reflink`; `_require_cp_reflink`; `rm -rf $testdir`; `mkdir $testdir`; `echo "Create the original files"`; `_require_congruent_file_oplen $TEST_DIR $blksz`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions; I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/578.out`; content dumps/hexdumps expose corruption or unexpected nonzero data; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
