# sources/test-tools/xfstests/tests/generic/315

## Purpose

fallocate/truncate tests with FALLOC_FL_KEEP_SIZE option Verify if the disk space is released after truncating a file back to the old smaller size. Before Linux 3.10, Btrfs/OCFS2 are test failed in this case Modify as appropriate Check the current avaliable disk space on $TEST_DIR 1024KiB at least Preallocate half size of the available disk space to a file starts from offset 0 with FALLOC_FL_KEEP_SIZE option on the test file system. It is registered with `_begin_fstest auto quick rw prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `315` plus `_begin_fstest auto quick rw prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`, `_require_xfs_io_command "falloc" "-k"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 15: `status=0 # success is the default!`
- Line 29: `avail_begin=`df -P $TEST_DIR | awk 'END {print $4}'``
- Line 39: `fsize=`_get_filesize $TEST_DIR/testfile.$seq``
- Line 47: `avail_done=`df -P $TEST_DIR | awk 'END {print $4}'``

## Control Flow

The visible phases are driven by echo markers such as line 25 `echo "Slience is golden"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 22: `_require_test`
- Line 23: `_require_xfs_io_command "falloc" "-k"`
- Line 29: `avail_begin=`df -P $TEST_DIR | awk 'END {print $4}'``
- Line 35: `$XFS_IO_PROG -f -c 'falloc -k 0 $(($avail_begin/2))' \`
- Line 43: `truncate -s 0 $TEST_DIR/testfile.$seq`
- Line 44: `_test_sync`
- Line 47: `avail_done=`df -P $TEST_DIR | awk 'END {print $4}'``

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `rw`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`, `_require_xfs_io_command "falloc" "-k"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Thin-provisioning tests depend on device-mapper target behavior, pool exhaustion semantics, and correct cleanup of temporary block devices.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
