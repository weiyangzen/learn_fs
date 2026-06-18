# sources/test-tools/xfstests/tests/generic/561

## Purpose

FS QA Test generic/561 Dedup & random I/O race test, do multi-threads fsstress and dedupe on same directory/files

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto stress dedupe unreliable_in_parallel`. It imports `./common/preamble`, `./common/filter`, `./common/reflink`. Prerequisite and skip gates include `_require_scratch_duperemove`. Local helper functions: `_cleanup`. External command surfaces and helper binaries visible in the source include `duperemove`, `fsstress`, `wait`, `mkdir`, `seq`, `cp`, `touch`, `sleep`, `umount`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `TEST_DIR`, `seqres.full`, `tmp`, `seq`, `TIME_FACTOR`, `LOAD_FACTOR`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_duperemove`; `_scratch_mkfs > $seqres.full 2>&1`; `_scratch_mount >> $seqres.full 2>&1`; `function end_test()`; `_kill_fsstress`; `rm -f $dupe_run`; `_pkill $dedup_bin >/dev/null 2>&1`; `wait $dedup_pids`; `rm -f $dedup_prog`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

shared extent, COW, or dedupe paths can corrupt unrelated file ranges or violate swapfile restrictions. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/561.out`; success is mostly silence after prerequisite and operation checks. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
