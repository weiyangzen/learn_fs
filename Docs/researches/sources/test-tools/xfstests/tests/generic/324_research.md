# sources/test-tools/xfstests/tests/generic/324

## Purpose

Sanity check for defrag utility. It is registered with `_begin_fstest auto fsr quick defrag prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `324` plus `_begin_fstest auto fsr quick defrag prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/defrag`. Capability gates: `_require_scratch`, `_require_defrag`, `_require_xfs_io_command "falloc"`. Local functions: `_workout`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 12: `PIDS=""`
- Line 24: `nr=$1`
- Line 38: `patt=`printf "0x%x" $i``
- Line 52: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 25 `echo "Defragment file with $nr * 2 fragments"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 18: `_require_scratch`
- Line 20: `_require_xfs_io_command "falloc"`
- Line 29: `$XFS_IO_PROG -f -c "falloc $((409600*i)) 4k" \`
- Line 33: `$XFS_IO_PROG -c "falloc 0 $((204800*nr))" \`
- Line 34: `$SCRATCH_MNT/test.$nr | _filter_xfs_io`
- Line 39: `$XFS_IO_PROG -c "pwrite -S $patt $((i*123400)) 1234" \`
- Line 40: `$SCRATCH_MNT/test.$nr | _filter_xfs_io`
- Line 47: `_scratch_mkfs >> $seqres.full 2>&1`
- Line 48: `_scratch_mount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `fsr`, `quick`, `defrag`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/defrag`, and uses capability gates such as `_require_scratch`, `_require_defrag`, `_require_xfs_io_command "falloc"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
