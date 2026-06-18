# sources/test-tools/xfstests/tests/generic/516

## Purpose

Ensuring that we cannot dedupe non-matching parts of files: - Fail to dedupe non-identical parts of two different files - Check that nothing changes in either file

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick dedupe clone fiemap`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`. Prerequisite and skip gates include `_require_test_dedupe`, `_require_congruent_file_oplen $TEST_DIR $blksz`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `seq`, `mkdir`, `stat`. Important harness variables and paths include `TEST_DIR`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test_dedupe`; `rm -rf $testdir`; `mkdir $testdir`; `echo "Create the original files"`; `_require_congruent_file_oplen $TEST_DIR $blksz`; `_pwrite_byte 0x61 $((blksz * 2)) $((blksz * 6)) $testdir/file1 >> $seqres.full`; `_pwrite_byte 0x61 $((blksz * 2)) $((blksz * 6)) $testdir/file2 >> $seqres.full`; `_pwrite_byte 0x62 $(((blksz * 6) - 33)) 1 $testdir/file2 >> $seqres.full`; `_test_cycle_mount`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/516.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
