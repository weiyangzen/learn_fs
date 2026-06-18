# sources/test-tools/xfstests/tests/generic/352

## Purpose

Test fiemap ioctl on heavily deduped file This test case will check if reserved extent map searching go without problem and return correct SHARED flag Which btrfs will soft lock up and return wrong shared flag Modify as appropriate The size is too small, this will result in an inline extent and then reflink will simply be a copy on btrfs, so exclude compression. It is registered with `_begin_fstest auto clone fiemap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `352` plus `_begin_fstest auto clone fiemap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/punch`. Capability gates: `_require_scratch_reflink`, `_require_xfs_io_command "fiemap"`, `_require_no_compress`, `_require_congruent_file_oplen $SCRATCH_MNT $blocksize`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 33: `blocksize=$(_get_file_block_size $SCRATCH_MNT)`
- Line 35: `file="$SCRATCH_MNT/tmp"`
- Line 39: `orig_nr=8192`
- Line 40: `orig_blocksize=4096`
- Line 41: `orig_last_extent=$(($orig_nr * $orig_blocksize / 512))`
- Line 42: `orig_end=$(($orig_last_extent + $orig_blocksize / 512 - 1))`
- Line 45: `nr=$(($orig_nr * $LOAD_FACTOR))`
- Line 46: `last_extent=$(($nr * $blocksize / 512))`

## Control Flow

The script runs linearly after the harness and requirement checks. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 14: `_begin_fstest auto clone fiemap`
- Line 23: `_require_scratch_reflink`
- Line 24: `_require_xfs_io_command "fiemap"`
- Line 30: `_scratch_mkfs > /dev/null 2>&1`
- Line 31: `_scratch_mount`
- Line 50: `_pwrite_byte 0xcdcdcdcd 0 $blocksize $file > /dev/null`
- Line 55: `_reflink_range $file 0 $file $(($i * $blocksize)) $blocksize > /dev/null`
- Line 60: `$XFS_IO_PROG -c "fiemap -v" $file | _filter_fiemap_flags > $tmp.out`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `clone`, `fiemap`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/punch`, and uses capability gates such as `_require_scratch_reflink`, `_require_xfs_io_command "fiemap"`, `_require_no_compress`, `_require_congruent_file_oplen $SCRATCH_MNT $blocksize`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Reflink coverage is sensitive to extent alignment, delayed allocation, unwritten extents, and page-size dependent block geometry, so comparisons against check files are the main correctness guard.
- Extent-map output is formatted and filtered, but the test still depends on stable extent flags, logical block addressing, and filesystem support for the ioctl under test.

## Test Signals

The pass signal is filtered extent-map output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
