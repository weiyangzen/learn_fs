# sources/test-tools/xfstests/tests/generic/277

## Purpose

Check if ctime update caused by chattr is written to disk. It is registered with `_begin_fstest auto ioctl quick metadata` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `277` plus `_begin_fstest auto ioctl quick metadata`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`. Capability gates: `_require_scratch`, `_require_chattr A`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 30: `ctime1=`stat -c %z $SCRATCH_MNT/tmp``
- Line 35: `ctime2=`stat -c %z $SCRATCH_MNT/tmp``
- Line 38: `ctime3=`stat -c %z $SCRATCH_MNT/tmp``
- Line 45: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 41 `echo "error: ctime not updated after chattr"`, line 43 `echo "error: on disk ctime not updated"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 15: `rm -f $SCRATCH_MNT/tmp*`
- Line 22: `_require_scratch`
- Line 25: `_scratch_mkfs > /dev/null 2>&1`
- Line 26: `_scratch_mount`
- Line 28: `touch $SCRATCH_MNT/tmp`
- Line 29: `_scratch_cycle_mount`
- Line 30: `ctime1=`stat -c %z $SCRATCH_MNT/tmp``
- Line 35: `ctime2=`stat -c %z $SCRATCH_MNT/tmp``
- Line 37: `_scratch_cycle_mount`
- Line 38: `ctime3=`stat -c %z $SCRATCH_MNT/tmp``

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `ioctl`, `quick`, `metadata`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, and uses capability gates such as `_require_scratch`, `_require_chattr A`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is stat/lstat metadata output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
