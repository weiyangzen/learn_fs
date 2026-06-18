# sources/test-tools/xfstests/tests/generic/240

## Purpose

Test that non-block-aligned aio+dio into holes does not leave zero'd out portions of the file QEMU IO to a file-backed device with misaligned partitions can send this sort of IO This test need only be run in the case where the logical block size of the device can be smaller than the file system block size. It is registered with `_begin_fstest auto aio quick rw` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `240` plus `_begin_fstest auto aio quick rw`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`, `_require_sparse_files`, `_require_aiodio aiodio_sparse2`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 32: `logical_block_size=`$here/src/min_dio_alignment $TEST_DIR $TEST_DEV``
- Line 33: `fs_block_size=`_get_block_size $TEST_DIR``
- Line 34: `file_size=$((8 * $fs_block_size))`
- Line 44: `status=$?`

## Control Flow

The visible phases are driven by echo markers such as line 27 `echo "Silence is golden."`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 23: `_require_test`
- Line 30: `rm -f $TEST_DIR/aiodio_sparse`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `aio`, `quick`, `rw`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`, `_require_sparse_files`, `_require_aiodio aiodio_sparse2`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
