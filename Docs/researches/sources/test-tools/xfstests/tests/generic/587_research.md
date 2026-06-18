# sources/test-tools/xfstests/tests/generic/587

## Purpose

Regression test to ensure that dquots are attached to the inode when we're performing unwritten extent conversion after a directio write and the extent mapping btree splits. On an unpatched kernel, the quota accounting will be become incorrect. This test accompanies the commit 2815a16d7ff623 "xfs: attach dquots and reserve quota blocks during unwritten conversion".

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick rw prealloc quota`. It imports `./common/preamble`, `./common/filter`, `./common/quota`. Prerequisite and skip gates include `_require_user`, `_require_quota`, `_require_xfs_io_command "falloc"`, `_require_scratch`, `_require_odirect`. Local helper functions: `check_quota_accounting`. External command surfaces and helper binaries visible in the source include `xfs_io`, `awk`, `stat`, `grep`, `seq`, `touch`, `chown`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `seqres.full`, `tmp`, `seq`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_user`; `_require_quota`; `_require_xfs_io_command "falloc"`; `_require_scratch`; `_require_odirect`; `writes a deterministic fsx replay script`; `printf("%s: quota blocks %dKiB, expected %dKiB!\n", qa_user, \$2, blocks);`; `ENDL`; `_scratch_mkfs > $seqres.full`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; enables quota accounting/enforcement state and adjusts grace timers or ownership/project metadata. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

I/O path races may be timing-sensitive and surface only under mmap, direct I/O, io_uring, or fsx replay stress; quota timer and enforcement semantics vary by filesystem and userspace quota tooling. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/587.out`; success is mostly silence after prerequisite and operation checks; grep-based checks assert expected metadata or data is still visible. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
