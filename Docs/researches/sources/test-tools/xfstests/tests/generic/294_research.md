# sources/test-tools/xfstests/tests/generic/294

## Purpose

Tests for EEXIST (not EROFS) for inode creations, if we ask to create an already-existing entity on an RO filesystem NFS will optimize away the on-the-wire lookup before attempting to create a new file (since that means an extra round trip). It is registered with `_begin_fstest auto quick` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `294` plus `_begin_fstest auto quick`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`, `_require_symlinks`, `_require_mknod`. Local functions: `_create_files`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 27: `THIS_TEST_DIR=$SCRATCH_MNT/$seq.test`
- Line 47: `status=0`

## Control Flow

Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 21: `_require_scratch`
- Line 25: `_scratch_mkfs > $seqres.full 2>&1 || _fail "Could not mkfs scratch device"`
- Line 31: `mknod $THIS_TEST_DIR/testnode c 1 3 2>&1 | _filter_mknod`
- Line 32: `mkdir $THIS_TEST_DIR/testdir`
- Line 33: `touch $THIS_TEST_DIR/testtarget`
- Line 34: `ln -s $THIS_TEST_DIR/testtarget $THIS_TEST_DIR/testlink 2>&1 | _filter_ln`
- Line 37: `_scratch_mount`
- Line 39: `rm -rf $THIS_TEST_DIR`
- Line 40: `mkdir $THIS_TEST_DIR || _fail "Could not create dir for test"`
- Line 42: `_create_files 2>&1 | _filter_scratch`
- Line 43: `_try_scratch_mount -o remount,ro || _fail "Could not remount scratch readonly"`
- Line 44: `_create_files 2>&1 | _filter_scratch`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`, `_require_symlinks`, `_require_mknod`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Symlink persistence tests are metadata-focused and can fail through lost directory updates, wrong target payloads, or fast/slow symlink representation differences.

## Test Signals

The pass signal is explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
