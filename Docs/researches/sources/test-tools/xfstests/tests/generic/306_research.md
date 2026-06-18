# sources/test-tools/xfstests/tests/generic/306

## Purpose

Test RW open of a device on a RO fs Modify as appropriate. It is registered with `_begin_fstest auto quick rw` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `306` plus `_begin_fstest auto quick rw`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`, `_require_test`, `_require_symlinks`, `_require_mknod`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 30: `DEVNULL=$SCRATCH_MNT/devnull`
- Line 31: `DEVZERO=$SCRATCH_MNT/devzero`
- Line 32: `SYMLINK=$SCRATCH_MNT/symlink`
- Line 33: `BINDFILE=$SCRATCH_MNT/bindfile`
- Line 34: `TARGET=$TEST_DIR/target`
- Line 76: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 50 `echo "== try to create new file"`, line 52 `echo "== pwrite to null device"`, line 54 `echo "== pread from zero device"`, line 57 `echo "== truncating write to null device"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 15: `_unmount $BINDFILE`
- Line 17: `rm -f $tmp.*`
- Line 25: `_require_scratch`
- Line 26: `_require_test`
- Line 36: `_scratch_mkfs > $seqres.full 2>&1`
- Line 37: `_scratch_mount`
- Line 39: `rm -f $DEVNULL $DEVZERO`
- Line 43: `touch $BINDFILE || _fail "Could not create bind mount file"`
- Line 44: `touch $TARGET || _fail "Could not create symlink target"`
- Line 45: `ln -s $TARGET $SYMLINK`
- Line 47: `_scratch_remount ro || _fail "Could not remount scratch readonly"`
- Line 51: `touch $SCRATCH_MNT/this_should_fail 2>&1 | _filter_scratch`
- Line 53: `$XFS_IO_PROG -c "pwrite 0 512" $DEVNULL | _filter_xfs_io`
- Line 73: `$XFS_IO_PROG -t -c "pwrite 0 512" $BINDFILE | _filter_xfs_io`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. It may also use `$TEST_DIR` for non-destructive helper programs or limit checks. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `rw`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`, `_require_test`, `_require_symlinks`, `_require_mknod`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Symlink persistence tests are metadata-focused and can fail through lost directory updates, wrong target payloads, or fast/slow symlink representation differences.

## Test Signals

The pass signal is explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
