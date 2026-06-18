# sources/test-tools/xfstests/tests/generic/530

## Purpose

Stress test creating a lot of unlinked O_TMPFILE files and recovering them after a crash, checking that we don't blow up the filesystem. This is sort of a performance test for the xfs unlinked inode backref patchset, but it applies to most other filesystems. Use only a single CPU to test the single threaded situation.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick shutdown unlink`. It imports `./common/preamble`. Prerequisite and skip gates include `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`, `_require_test_program "t_open_tmpfiles"`. No major local helper functions are defined; the scenario is driven directly by the top-level shell flow. External command surfaces and helper binaries visible in the source include `t_open_tmpfiles`, `sort`, `seq`, `umount`. Important harness variables and paths include `SCRATCH_MNT`, `TEST_DIR`, `seqres.full`, `tmp`, `seq`, `LOAD_FACTOR`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch`; `_require_scratch_shutdown`; `_require_metadata_journaling`; `_require_test_program "t_open_tmpfiles"`; `_scratch_mkfs $(_scratch_mkfs_concurrency_options) >> $seqres.full 2>&1`; `_scratch_mount`; `max_files=$((50000 * LOAD_FACTOR))`; `max_allowable_files=$(( $(cat /proc/sys/fs/file-max) / 2 ))`; `test $max_allowable_files -gt 0 && test $max_files -gt $max_allowable_files && max_files=$max_allowable_files`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses the configured test filesystem under `TEST_DIR` without necessarily reformatting it; injects block-device, power-fail, shutdown, or thin-provisioning behavior to validate recovery paths. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

ordering bugs in journal replay or fsync logging can lose metadata or data after simulated power loss. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/530.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
