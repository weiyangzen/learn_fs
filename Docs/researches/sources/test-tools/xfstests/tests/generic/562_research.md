# sources/test-tools/xfstests/tests/generic/562

## Purpose

Test that if we clone a file with some large extents into a file that has many small extents, when the fs is nearly full, the clone operation does not fail and produces the correct result.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto clone punch`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`. Prerequisite and skip gates include `_require_scratch_reflink`, `_require_test_program "punch-alternating"`, `_require_xfs_io_command "fpunch"`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `xfs_io`, `punch-alternating`, `grep`, `mount`, `od`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`, `FSTYP`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_fixed_by_fs_commit xfs 7ce31f20a077 "xfs: don't drop errno values when we fail to ficlone the entire range"`; `_require_scratch_reflink`; `_require_test_program "punch-alternating"`; `_require_xfs_io_command "fpunch"`; `_scratch_mkfs_sized $((590 * 1024 * 1024)) >>$seqres.full 2>&1`; `_scratch_mount`; `$XFS_IO_PROG -f -c "pwrite -S 0xe5 -b $file_size 0 $file_size" $SCRATCH_MNT/foo >>/dev/null`; `$here/src/punch-alternating $SCRATCH_MNT/foo >> $seqres.full`; `$XFS_IO_PROG -f -c "pwrite -S 0xc7 -b $file_size 0 $file_size" $SCRATCH_MNT/bar >>/dev/null`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/562.out`; content dumps/hexdumps expose corruption or unexpected nonzero data; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
