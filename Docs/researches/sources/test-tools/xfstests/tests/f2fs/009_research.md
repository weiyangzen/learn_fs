# sources/test-tools/xfstests/tests/f2fs/009

## Purpose

This is a regression test to check whether fsck can handle corrupted nlinks correctly, it uses inject.f2fs to inject nlinks w/ wrong value, and expects fsck.f2fs can detect such corruption and do the repair.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick`. Important local functions are `_cleanup`, `check_links`, `inject_and_check`. Key xfstests/helper interfaces include `_check_scratch_fs` (runs scratch filesystem consistency checking), `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_require_command` (checks availability of an external command), `_scratch_mount` (mounts the scratch filesystem). External or helper commands visible in the body include `find`, `ln`, `mkdir`, `rm`, `stat`, `touch`. Significant variables include `status`.

## Control Flow

The script sources `./common/preamble`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch`; `_require_inject_f2fs_command node i_links`; `_require_command "$(type -P socket)" socket`; `_fixed_by_git_commit f2fs-tools 958cd6e \`; `filename=$SCRATCH_MNT/foo`; `hardlink=$SCRATCH_MNT/bar`; `_cleanup()`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, fio verification state for direct/atomic I/O. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_command`, `_require_inject_f2fs_command`, `_require_scratch`. The test integrates with common xfstests libraries through `./common/preamble` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: prints `Silence is golden` after all checks pass; runs filesystem consistency checking; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
