# sources/test-tools/xfstests/tests/generic/062

## Purpose

Exercises the getfattr/setfattr tools Derived from tests originally written by Andreas Gruenbacher for ext2

## Important APIs, Types, and Functions

This is a bash xfstests case in the `generic` suite. The harness entry and tags are `_begin_fstest attr udf auto quick`. Important local functions are `_backup`, `_cleanup`, `_create_test_bed`, `_extend_test_bed`, `getfattr`, `invalid_attribute_filter`, and others. Key xfstests/helper interfaces include `_scratch_unmount` (unmounts scratch to force persistence checks), `_require_scratch` (requires a disposable scratch filesystem), `_filter_scratch` (normalizes scratch paths in stdout), `_scratch_mount` (mounts the scratch filesystem), `_require_attrs` (requires extended attribute support). External or helper commands visible in the body include `cp`, `diff`, `find`, `grep`, `ln`, `mkdir`, `rm`, `sed`, `touch`. Significant variables include `ATTR_FILTER`, `ATTR_MODES`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/attr`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_cleanup()`; `echo; echo "*** unmount"`; `_scratch_unmount 2>/dev/null`; `rm -f $tmp.*`; `_getfattr --absolute-names -dh $@ 2>&1 | _filter_scratch`; `_create_test_bed()`; `echo "*** create test bed"`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_attrs`, `_require_mknod`, `_require_scratch`, `_require_symlinks`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/attr` and with suite-specific filesystem features selected by the `generic` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, timing or background-process races can make failures intermittent. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: uses byte-for-byte comparison of generated and expected data; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
