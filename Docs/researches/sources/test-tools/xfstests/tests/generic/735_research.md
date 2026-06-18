# sources/test-tools/xfstests/tests/generic/735

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/735`. Append writes to a file with logical block numbers close to 0xffffffff and observe if a kernel crash is caused by ext4_lblk_t overflow triggering BUG_ON at ext4_mb_new_inode_pa(). This is a regression test for commit bc056e7163ac ("ext4: fix BUG in ext4_mb_new_inode_pa() due to overflow") commit 2dcf5fde6dff ("ext4: prevent the normalized size from exceeding EXT_MAX_BLOCKS") It is registered with `_begin_fstest auto quick insert prealloc`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 58 source line(s).
- Harness registration: `_begin_fstest auto quick insert prealloc`.
- Imported common libraries: `./common/preamble`, `./common/populate`.
- Capability and skip gates: `_fixed_by_kernel_commit bc056e7163ac "ext4: fix BUG in ext4_mb_new_inode_pa() due to overflow"`, `_fixed_by_kernel_commit 2dcf5fde6dff "ext4: prevent the normalized size from exceeding EXT_MAX_BLOCKS"`, `_require_odirect`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "finsert"`, `_require_max_file_range_blocks $(( (1 << 32) - 1 ))`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576	# finsert at 1M`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `dev_size=$((80 * 1024 * 1024))`
- `file_blksz="$(_get_file_block_size ${SCRATCH_MNT})"`
- `max_pos=$(( 0xffffffff * file_blksz ))`
- `finsert_len=$(( max_pos - ((10 + 2) << 20) ))`
- `nr_free=$(stat -f -c '%f' ${SCRATCH_MNT})`

## Control Flow

- Capability gating runs first through `_fixed_by_kernel_commit bc056e7163ac "ext4: fix BUG in ext4_mb_new_inode_pa() due to overflow"`, `_fixed_by_kernel_commit 2dcf5fde6dff "ext4: prevent the normalized size from exceeding EXT_MAX_BLOCKS"`, `_require_odirect`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "finsert"`, plus 2 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 54: echo "Silence is golden"`
- Key operational lines include:
- `line 23: _require_xfs_io_command "falloc"`
- `line 24: _require_xfs_io_command "finsert"`
- `line 28: _scratch_mkfs_sized $dev_size >>$seqres.full 2>&1`
- `line 30: _scratch_mount`
- `line 31: _require_congruent_file_oplen $SCRATCH_MNT 1048576 # finsert at 1M`
- `line 35: $XFS_IO_PROG -f -c "falloc 0 1M" "${SCRATCH_MNT}/tmp" >> $seqres.full`
- `line 38: $XFS_IO_PROG -f -c "falloc 0 10M" "${SCRATCH_MNT}/file" >> $seqres.full`
- `line 40: finsert_len=$(( max_pos - ((10 + 2) << 20) ))`
- `line 41: $XFS_IO_PROG -f -c "finsert 1M ${finsert_len}" "${SCRATCH_MNT}/file" >> $seqres.full`
- `line 44: nr_free=$(stat -f -c '%f' ${SCRATCH_MNT})`
- `line 46: _scratch_sync`
- `line 52: $XFS_IO_PROG -c "open -ad ${SCRATCH_MNT}/file" -c "pwrite -S 0xff 0 $((2 * file_blksz))" >> $seqres.full`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick insert prealloc`, common helper libraries (`./common/preamble`, `./common/populate`), and the golden-output file `sources/test-tools/xfstests/tests/generic/735.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_kernel_commit bc056e7163ac "ext4: fix BUG in ext4_mb_new_inode_pa() due to overflow"`, `_fixed_by_kernel_commit 2dcf5fde6dff "ext4: prevent the normalized size from exceeding EXT_MAX_BLOCKS"`, `_require_odirect`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "finsert"`, `_require_max_file_range_blocks $(( (1 << 32) - 1 ))`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576	# finsert at 1M`.

## Risks and Edge Cases

- Direct/AIO coverage depends on alignment, device logical block size, page size, and filesystem direct-I/O semantics.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 735; Silence is golden'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
