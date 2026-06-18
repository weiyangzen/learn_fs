# sources/test-tools/xfstests/tests/generic/612

## Purpose

Regression test for reflink corruption present as of: 78f0cc9d55cb "xfs: don't use delalloc extents for COW on files with extsize hints" and (inadvertently) fixed as of: 36adcbace24e "xfs: fill out the srcmap in iomap_begin" upstream, and in the 5.4 stable tree with: aee38af574a1 "xfs: trim IO to found COW extent limit"

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick clone`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`. Prerequisite and skip gates include `_require_test`, `_require_test_reflink`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xfs_io`, `seq`, `mkdir`, `cp`, `mount`. Important harness variables and paths include `TEST_DIR`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `_require_test_reflink`; `mkdir -p $DIR`; `rm -f $DIR/a $DIR/b`; `$XFS_IO_PROG -c "extsize 1048576" $DIR >/dev/null 2>&1`; `$XFS_IO_PROG -c "cowextsize 1048576" $DIR >/dev/null 2>&1`; `echo "Create file b"`; `$XFS_IO_PROG -f -c "pwrite -S 0x0 0 2m" -c fsync $DIR/b | _filter_xfs_io`; `echo "Reflink copy from b to a"`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/612.out`; content dumps/hexdumps expose corruption or unexpected nonzero data. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
