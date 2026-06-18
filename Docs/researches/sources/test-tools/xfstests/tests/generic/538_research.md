# sources/test-tools/xfstests/tests/generic/538

## Purpose

Non-block-aligned direct AIO write test with an initial truncate i_size. Uncover "ext4: Fix data corruption caused by unaligned direct AIO": (Ext4 needs to serialize unaligned direct AIO because the zeroing of partial blocks of two competing unaligned AIOs can result in data corruption. However it decides not to serialize if the potentially unaligned aio is past i_size with the rationale that no pending writes are possible past i_size. Unfortunately if the i_size is not block aligned and the second unaligned write lands past i_size, but still into the same block, it has the potential of corrupting the previous unaligned write to the same block.)

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick aio`. It imports `./common/preamble`, `./common/filter`. Prerequisite and skip gates include `_require_test`, `_require_aiodio aio-dio-write-verify`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `min_dio_alignment`, `truncate`, `seq`. Important harness variables and paths include `TEST_DIR`, `TEST_DEV`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_test`; `_require_aiodio aio-dio-write-verify`; `diosize=`$here/src/min_dio_alignment $TEST_DIR $TEST_DEV``; `blocksize=`_get_block_size $TEST_DIR``; `bufsize=$((blocksize * 2))`; `truncsize=$((bufsize+diosize))`; `_notrun "Need device logical block size($diosize) < fs block size($blocksize)"`; `rm -rf $localfile 2>/dev/null`; `$AIO_TEST -a size=$bufsize,off=0 -a size=$bufsize,off=$bufsize $localfile`.

## State and Persistence Behavior

The test uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/538.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
