# sources/test-tools/xfstests/tests/generic/298

## Purpose

See how well reflink handles SIGKILL in the middle of a slow reflink. It is registered with `_begin_fstest auto clone` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `298` plus `_begin_fstest auto clone`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/reflink`. Capability gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_command "$TIMEOUT_PROG" "timeout"`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 34: `testdir=$SCRATCH_MNT/test-$seq`
- Line 38: `blksz="$(_get_block_size $testdir)"`
- Line 41: `fnr=26 # 2^26 reflink extents should be enough to find a slow op?`
- Line 42: `timeout=8 # guarantee a good long run...`
- Line 46: `n=$(( (2 ** i) * blksz))`
- Line 50: `before=$(stat -c '%Y' $TEST_DIR/before)`
- Line 51: `after=$(stat -c '%Y' $TEST_DIR/after)`
- Line 52: `delta=$((after - before))`

## Control Flow

The visible phases are driven by echo markers such as line 30 `echo "Format and mount"`, line 37 `echo "Create a one block file"`, line 43 `echo "Find a reflink size that takes a long time"`, line 45 `echo " ++ Reflink size $i, $((2 ** i)) blocks" >> $seqres.full`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 16: `rm -rf $tmp.* $TEST_DIR/before $TEST_DIR/after`
- Line 24: `_require_scratch_reflink`
- Line 25: `_require_cp_reflink`
- Line 30: `echo "Format and mount"`
- Line 31: `_scratch_mkfs > $seqres.full 2>&1`
- Line 32: `_scratch_mount >> $seqres.full 2>&1`
- Line 35: `mkdir $testdir`
- Line 39: `_pwrite_byte 0x61 0 $blksz $testdir/file1 >> $seqres.full`
- Line 47: `touch $TEST_DIR/before`
- Line 48: `$XFS_IO_PROG -f -c "reflink $testdir/file1 0 $n $n" $testdir/file1 >> $seqres.full 2>&1`
- Line 49: `touch $TEST_DIR/after`
- Line 50: `before=$(stat -c '%Y' $TEST_DIR/before)`
- Line 51: `after=$(stat -c '%Y' $TEST_DIR/after)`
- Line 64: `after=$(stat -c '%Y' $TEST_DIR/after)`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. It may also use `$TEST_DIR` for non-destructive helper programs or limit checks. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `clone`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/reflink`, and uses capability gates such as `_require_scratch_reflink`, `_require_cp_reflink`, `_require_command "$TIMEOUT_PROG" "timeout"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is stat/lstat metadata output, explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
