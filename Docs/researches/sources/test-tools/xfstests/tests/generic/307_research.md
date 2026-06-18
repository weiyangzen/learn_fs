# sources/test-tools/xfstests/tests/generic/307

## Purpose

Check if ctime is updated and written to disk after setfacl Regression test for the following extN commits c6ac12a ext4: update ctime when changing the file's permission by setfacl 30e2bab ext3: update ctime when changing the file's permission by setfacl 523825b ext2: update ctime when changing the file's permission by setfacl Based on test 277. It is registered with `_begin_fstest auto quick acl` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `307` plus `_begin_fstest auto quick acl`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`. Capability gates: `_require_scratch`, `_require_acls`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 30: `testfile=$SCRATCH_MNT/testfile.$seq`
- Line 42: `ctime1=`stat -c %Z $testfile``
- Line 46: `ctime2=`stat -c %Z $testfile``
- Line 49: `ctime3=`stat -c %Z $testfile``
- Line 56: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 35 `echo "Silence is golden"`, line 52 `echo "error: ctime not updated after setfacl"`, line 54 `echo "error: on disk ctime not updated"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 23: `rm -f $testfile`
- Line 32: `_require_scratch`
- Line 37: `_scratch_mkfs >/dev/null 2>&1`
- Line 38: `_scratch_mount >/dev/null 2>&1`
- Line 40: `touch $testfile`
- Line 41: `_scratch_cycle_mount`
- Line 42: `ctime1=`stat -c %Z $testfile``
- Line 46: `ctime2=`stat -c %Z $testfile``
- Line 48: `_scratch_cycle_mount`
- Line 49: `ctime3=`stat -c %Z $testfile``

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `acl`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, and uses capability gates such as `_require_scratch`, `_require_acls`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is stat/lstat metadata output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
