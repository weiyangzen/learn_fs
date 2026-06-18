# sources/test-tools/xfstests/tests/generic/286

## Purpose

SEEK_DATA/SEEK_HOLE copy tests seek_copy_test_01: tests file with holes and written data extents verify results: 1. file size is identical 2. perform cmp(1) to compare SRC and DEST file byte by byte. It is registered with `_begin_fstest auto quick other seek prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `286` plus `_begin_fstest auto quick other seek prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`, `_require_xfs_io_command "falloc"`, `_require_seek_data_hole`, `_require_test_program "seek_copy_test"`. Local functions: `_cleanup`, `test01`, `test02`, `test03`, `test04`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 20: `src=$TEST_DIR/seek_copy_testfile`
- Line 21: `dest=$TEST_DIR/seek_copy_testfile.dest`
- Line 39: `write_cmd="-c \"truncate 100m\""`
- Line 41: `offset=$(($i * $((1 << 20))))`
- Line 42: `write_cmd="$write_cmd -c \"pwrite $offset 1m\""`
- Line 67: `write_cmd="-c \"truncate 200m\""`
- Line 69: `offset=$(($((6 << 20)) + $i * $((1 << 20))))`
- Line 70: `write_cmd="$write_cmd -c \"falloc $offset 3m\" -c \"pwrite $offset 1m\""`

## Control Flow

The visible phases are driven by echo markers such as line 45 `echo "*** test01() create sparse file ***" >>$seqres.full`, line 48 `echo "*** test01() create sparse file done ***" >>$seqres.full`, line 49 `echo >>$seqres.full`, line 73 `echo "*** test02() create sparse file ***" >>$seqres.full`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 16: `_require_test`
- Line 17: `_require_xfs_io_command "falloc"`
- Line 20: `src=$TEST_DIR/seek_copy_testfile`
- Line 21: `dest=$TEST_DIR/seek_copy_testfile.dest`
- Line 23: `_require_test_program "seek_copy_test"`
- Line 28: `rm -f $src $dest`
- Line 37: `rm -f $src $dest`
- Line 39: `write_cmd="-c \"truncate 100m\""`
- Line 51: `$here/src/seek_copy_test $src $dest`
- Line 56: `cmp $src $dest || _fail "TEST01: file bytes check failed"`
- Line 65: `rm -rf $src $dest`
- Line 67: `write_cmd="-c \"truncate 200m\""`
- Line 70: `write_cmd="$write_cmd -c \"falloc $offset 3m\" -c \"pwrite $offset 1m\""`
- Line 168: `cmp $src $dest || _fail "TEST04: file bytes check failed"`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `other`, `seek`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`, `_require_xfs_io_command "falloc"`, `_require_seek_data_hole`, `_require_test_program "seek_copy_test"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
