# sources/test-tools/xfstests/tests/generic/641

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/641`. Test small swapfile which doesn't contain even a single page-aligned contiguous range of blocks. This case covered commit 5808fecc5723 ("iomap: Fix negative assignment to unsigned sis->pages in iomap_swapfile_activate"). It is registered with `_begin_fstest auto quick swap collapse`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 75 source line(s).
- Harness registration: `_begin_fstest auto quick swap collapse`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_scratch`, `_require_scratch_swapfile`, `_require_test_program mkswap`, `_require_test_program swapon`, `_require_xfs_io_command fcollapse`, `_notrun "Can't make filesystem block size < page size."`, `_notrun "Can't force 1024-byte file block size."`.
- Local shell functions: `make_unaligned_swapfile`.
- External `$here/src` helpers: `$here/src/mkswap $fname`, `$here/src/swapon $swapfile`.
- Notable variables and constants:
- `psize=`_get_page_size``
- `bsize=`_get_file_block_size $SCRATCH_MNT``
- `bsize=`_get_file_block_size $SCRATCH_MNT``
- `swapfile=$SCRATCH_MNT/$seq.swapfile`
- `swapsize=$(awk -v fname="$swapfile" '{if ($1~fname) print $3}' /proc/swaps)`
- `swapsize=$((swapsize * 1024))`
- `filesize=$(_get_filesize $swapfile)`

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_scratch_swapfile`, `_require_test_program mkswap`, `_require_test_program swapon`, `_require_xfs_io_command fcollapse`, plus 2 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 68: echo "Allocated swap size($swapsize) shouldn't be greater than swapfile size($filesize)"`
- Key operational lines include:
- `line 18: _require_scratch_swapfile`
- `line 30: $XFS_IO_PROG -f -t -c "pwrite 0 $(((psize + bsize) * n))" $fname >> $seqres.full 2>&1`
- `line 32: $XFS_IO_PROG -c "fcollapse $(((psize - bsize) * i)) $bsize" $fname`
- `line 39: _scratch_mkfs >> $seqres.full 2>&1`
- `line 40: _scratch_mount`
- `line 46: _scratch_unmount`
- `line 47: _scratch_mkfs_blocksized 1024 >> $seqres.full 2>&1`
- `line 51: _scratch_mount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick swap collapse`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/641.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_scratch_swapfile`, `_require_test_program mkswap`, `_require_test_program swapon`, `_require_xfs_io_command fcollapse`, `_notrun "Can't make filesystem block size < page size."`, `_notrun "Can't force 1024-byte file block size."`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 641; swapon: Invalid argument'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
