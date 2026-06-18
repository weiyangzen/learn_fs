# sources/test-tools/xfstests/tests/generic/317

## Purpose

Check uid/gid to/from disk with a user namespace. A new file will be created from inside a userns. We check that the uid/gid is correct from both inside the userns and also from init_user_ns We will then unmount and remount the file system and check the uid/gid from both inside the userns and from init_user_ns to show that the correct uid was flushed and brought back from disk only Linux supports user namespace. It is registered with `_begin_fstest auto metadata quick` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `317` plus `_begin_fstest auto metadata quick`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`. Capability gates: `_require_scratch`, `_require_user`, `_require_ugid_map`, `_require_userns`, `_require_chown`, `_require_use_local_uidgid`. Local functions: `_cleanup`, `_filter_output`, `_print_numeric_uid`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 28: `file=$SCRATCH_MNT/file1`
- Line 40: `qa_user_id=`id -u $qa_user``
- Line 82: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 51 `echo "From init_user_ns"`, line 54 `echo "From user_ns"`, line 62 `echo "*** MKFS ***" >>$seqres.full`, line 63 `echo "" >>$seqres.full`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 21: `_scratch_unmount >/dev/null 2>&1`
- Line 34: `_require_scratch`
- Line 38: `_require_chown`
- Line 42: `_filter_output()`
- Line 52: `$here/src/lstat64 $file |head -3 |_filter_output`
- Line 58: `$here/src/nsexec -s -U -M "0 $qa_user_id 1000" -G "0 $qa_user_id 1000" src/lstat64 $file |head -3 |_filter_output`
- Line 61: `_scratch_unmount >/dev/null 2>&1`
- Line 64: `_scratch_mkfs >>$seqres.full 2>&1 || _fail "mkfs failed"`
- Line 65: `_scratch_mount`
- Line 66: `chmod 777 $SCRATCH_MNT`
- Line 69: `$here/src/nsexec -s -U -M "0 $qa_user_id 1000" -G "0 $qa_user_id 1000" touch $file`
- Line 74: `echo "*** Remounting ***"`
- Line 76: `_scratch_sync`
- Line 81: `_scratch_unmount >/dev/null 2>&1`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `metadata`, `quick`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, and uses capability gates such as `_require_scratch`, `_require_user`, `_require_ugid_map`, `_require_userns`, `_require_chown`, `_require_use_local_uidgid`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is stat/lstat metadata output, explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
