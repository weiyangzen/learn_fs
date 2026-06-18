# sources/test-tools/xfstests/tests/generic/643

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/643`. Regression test for commit: 36ca7943ac18 ("mm/swap: consider max pages in iomap_swapfile_add_extent") Xu Yu found that the iomap swapfile activation code failed to constrain itself to activating however many swap pages that the mm asked us for. This is an deviation in behavior from the classic swapfile code. It also leads to kernel memory corruption if the swapfile is cleverly constructed. It is registered with `_begin_fstest auto swap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 62 source line(s).
- Harness registration: `_begin_fstest auto swap`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_scratch_swapfile`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `swapfile=$SCRATCH_MNT/386spart.par`
- `before_blocks=$(_format_swapfile $swapfile 1m)`
- `page_size=$(getconf PAGE_SIZE)`
- `after_blocks=$(swapon --show --bytes |grep $swapfile | awk '{print $3}')`
- `page_variance=$(( page_size / 512 ))`

## Control Flow

- Capability gating runs first through `_require_scratch_swapfile`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- User-visible phase markers include:
- `line 59: echo "pagesize: $page_size; before: $before_blocks; after: $after_blocks" >> $seqres.full`
- Key operational lines include:
- `line 29: _require_scratch_swapfile`
- `line 31: _scratch_mkfs >> $seqres.full`
- `line 32: _scratch_mount >> $seqres.full`
- `line 43: $XFS_IO_PROG -f -c 'pwrite 1m 1m' $swapfile >> $seqres.full`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto swap`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/643.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_swapfile`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 643; swap blocks is in range'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
