# sources/test-tools/xfstests/tests/ext4/061

## Purpose

This test does a lot of parallel RWF_ATOMIC IO on a preallocated file to stress the write and end-io unwritten conversion code paths. We brute force this for all possible blocksize and clustersizes and after each iteration we ensure the data was not torn or corrupted using fio crc verification. Note that in this test we use overlapping atomic writes of same io size. Although RWF_ATOMIC does not generally promise serialization of racing writes, the test relies on equal-sized overlapping atomic writes to stress ext4 and block-layer no-tear behavior under NVMe/SCSI-style power-fail atomicity.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `ext4` suite. The harness entry and tags are `_begin_fstest auto rw stress atomicwrites`. Important local functions are `create_fio_aw_config`, `create_fio_configs`, `create_fio_verify_config`, `run_test`, `run_test_one`. Key xfstests/helper interfaces include `_require_scratch_write_atomic` (requires filesystem atomic-write capability), `_require_fio_atomic_writes` (checks fio atomic write support), `_scratch_mkfs_ext4` (formats scratch specifically as ext4), `_try_scratch_mount` (attempts to mount scratch and lets the test decide skip/fail behavior), `_scratch_unmount` (unmounts scratch to force persistence checks). External or helper commands visible in the body include `touch`. Significant variables include `FIO_LOAD`, `MKFS_OPTIONS`, `SIZE`, `bs`, `size`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/atomicwrites`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch_write_atomic`; `_require_fio_atomic_writes`; `_require_aiodio`; `_scratch_mkfs > /dev/null 2>&1 || \`; `_notrun "mkfs failed"`; `_try_scratch_mount || \`; `_notrun "mount failed"`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, fio verification state for direct/atomic I/O. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_aiodio`, `_require_fio`, `_require_fio_atomic_writes`, `_require_scratch_write_atomic`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/atomicwrites` and with suite-specific filesystem features selected by the `ext4` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent, stress-tool behavior and kernel timing can expose nondeterminism. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
