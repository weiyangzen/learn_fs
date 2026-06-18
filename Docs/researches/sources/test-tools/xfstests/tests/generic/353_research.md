# sources/test-tools/xfstests/tests/generic/353

## Purpose

Check if fiemap ioctl returns correct SHARED flag on reflinked file before and after sync the fs Btrfs has a bug in checking shared extent, which can only handle metadata already committed to disk, but not delayed extent tree modification This caused SHARED flag only occurs after sync Modify as appropriate. It is registered with `_begin_fstest auto quick clone fiemap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `353` plus `_begin_fstest auto quick clone fiemap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/punch`. Capability gates: `_require_scratch_reflink`, `_require_xfs_io_command "fiemap"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 30: `blocksize=$(_get_file_block_size $SCRATCH_MNT)`
- Line 32: `file1="$SCRATCH_MNT/file1"`
- Line 33: `file2="$SCRATCH_MNT/file2"`
- Line 34: `extmap1="$SCRATCH_MNT/extmap1"`
- Line 35: `extmap2="$SCRATCH_MNT/extmap2"`
- Line 60: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 57 `echo "Silence is golden"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 15: `_begin_fstest auto quick clone fiemap`
- Line 24: `_require_scratch_reflink`
- Line 25: `_require_xfs_io_command "fiemap"`
- Line 27: `_scratch_mkfs > /dev/null 2>&1`
- Line 28: `_scratch_mount`
- Line 38: `_pwrite_byte 0xcdcdcdcd 0 $blocksize $file1 > /dev/null`
- Line 41: `_reflink_range $file1 0 $file2 0 $blocksize > /dev/null`
- Line 44: `$XFS_IO_PROG -c "fiemap -v" $file1 | _filter_fiemap_flags > $extmap1`
- Line 45: `$XFS_IO_PROG -c "fiemap -v" $file2 | _filter_fiemap_flags > $extmap2`
- Line 47: `cmp -s $extmap1 $extmap2 || echo "mismatched extent maps before sync"`
- Line 51: `_scratch_sync`
- Line 52: `$XFS_IO_PROG -c "fiemap -v" $file1 | _filter_fiemap_flags > $extmap1`
- Line 53: `$XFS_IO_PROG -c "fiemap -v" $file2 | _filter_fiemap_flags > $extmap2`
- Line 55: `cmp -s $extmap1 $extmap2 || echo "mismatched extent maps after sync"`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `clone`, `fiemap`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/punch`, and uses capability gates such as `_require_scratch_reflink`, `_require_xfs_io_command "fiemap"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Extent-map output is formatted and filtered, but the test still depends on stable extent flags, logical block addressing, and filesystem support for the ioctl under test.

## Test Signals

The pass signal is byte-for-byte `cmp` checks against companion files, filtered extent-map output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
