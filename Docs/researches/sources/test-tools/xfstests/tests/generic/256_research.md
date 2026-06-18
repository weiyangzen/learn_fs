# sources/test-tools/xfstests/tests/generic/256

## Purpose

Test Full File System Hole Punching _test_full_fs_punch() This function will test that a hole may be punched even when the file system is full. Reserved blocks should be used to allow a punch hole to proceed even when there is not enough blocks to further fragment the file. To test this, this function will fragment the file system by punching holes in regular intervals and filling the file system between punches. It is registered with `_begin_fstest auto quick punch` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `256` plus `_begin_fstest auto quick punch`. Imported libraries: `. ./common/preamble`, `. ./common/populate`, `. ./common/filter`, `. ./common/punch`. Capability gates: `_require_xfs_io_command "fpunch"`, `_require_scratch`, `_require_user`, `_require_test`. Local functions: `_test_full_fs_punch`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 23: `testfile=$TEST_DIR/256.$$`
- Line 60: `start_time="$(date +%s)"`
- Line 61: `stop_time=$(( start_time + (30 * TIME_FACTOR) ))`
- Line 75: `rc=$?`
- Line 81: `hole_offset=$(( $hole_offset + $hole_len + $hole_interval ))`
- Line 95: `block_size=`_get_block_size $SCRATCH_MNT``
- Line 98: `status=0 ; exit`

## Control Flow

The visible phases are driven by echo markers such as line 50 `echo "USAGE: _test_full_fs_punch hole_len hole_interval iterations file_name block_size"`, line 77 `echo Punch hole failed`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 18: `_require_xfs_io_command "fpunch"`
- Line 19: `_require_scratch`
- Line 21: `_require_test`
- Line 35: `_test_full_fs_punch()`
- Line 50: `echo "USAGE: _test_full_fs_punch hole_len hole_interval iterations file_name block_size"`
- Line 54: `rm -f $file_name &> /dev/null`
- Line 56: `$XFS_IO_PROG -f -c "pwrite 0 $file_len" \`
- Line 57: `-c "fsync" $file_name &> /dev/null`
- Line 58: `chmod 666 $file_name`
- Line 74: `_user_do "$XFS_IO_PROG -f -c \"fpunch $hole_offset $hole_len\" $file_name"`
- Line 89: `_scratch_unmount &> /dev/null`
- Line 90: `_scratch_mkfs_sized $(( 1536 * 1024 * 1024 )) &> /dev/null`
- Line 91: `_scratch_mount`
- Line 96: `_test_full_fs_punch $(( $block_size * 2 )) $block_size 500 $SCRATCH_MNT/252.$$ $block_size`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. It may also use `$TEST_DIR` for non-destructive helper programs or limit checks. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `punch`, imports `. ./common/preamble`, `. ./common/populate`, `. ./common/filter`, `. ./common/punch`, and uses capability gates such as `_require_xfs_io_command "fpunch"`, `_require_scratch`, `_require_user`, `_require_test`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
