# sources/test-tools/xfstests/tests/generic/493

## Purpose

Check that we can't dedupe a swapfile.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick swap dedupe`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`. Prerequisite and skip gates include `_require_scratch_swapfile`, `_require_scratch_dedupe`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `chattr`, `mount`, `seq`, `mkdir`, `swapon`, `touch`, `cp`, `swapoff`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_swapfile`; `_require_scratch_dedupe`; `echo "Format and mount"`; `_scratch_mkfs > $seqres.full 2>&1`; `_scratch_mount >> $seqres.full 2>&1`; `mkdir "$testdir"`; `echo "Initialize file"`; `_format_swapfile "$testdir/file1" $((blocks * blksz)) > /dev/null`; `swapon "$testdir/file1"`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; temporarily activates swap files and must clean them with `swapoff`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

active swapfiles must reject extent-changing operations and require page-size/block-size compatibility; shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/493.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
