# sources/test-tools/xfstests/tests/generic/515

## Purpose

Ensure that reflinking into a file well beyond EOF zeroes everything between the old EOF and the start of the newly linked chunk. This is an adaptation of a reproducer script that Eric Sandeen formulated from a stale data exposure bug uncovered by shared/010.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick clone prealloc`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`. Prerequisite and skip gates include `_require_scratch_reflink`, `_require_xfs_io_command "falloc"`, `_require_congruent_file_oplen $SCRATCH_MNT $blksz`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xfs_io`, `stat`, `od`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_reflink`; `_require_xfs_io_command "falloc"`; `$XFS_IO_PROG -c "pwrite -S 0x58 -b 1m 0 300m" $SCRATCH_DEV >> $seqres.full`; `_scratch_mkfs_sized $((300 * 1048576)) >>$seqres.full 2>&1`; `_scratch_mount`; `_require_congruent_file_oplen $SCRATCH_MNT $blksz`; `$XFS_IO_PROG -f -c "pwrite -S 0x72 0 $blksz" $DONOR1 >> $seqres.full`; `$XFS_IO_PROG -f -c "falloc -k $((blksz*2)) $blksz" -c "pwrite -S 0x57 $((blksz*16)) 8192" -c "fdatasync" -c 'stat' -c "reflink $DONOR1 0 ...`; `od -tx1 -Ad -c $TARGET >> $seqres.full`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/515.out`; content dumps/hexdumps expose corruption or unexpected nonzero data. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
