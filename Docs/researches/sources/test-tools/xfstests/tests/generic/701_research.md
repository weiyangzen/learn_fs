# sources/test-tools/xfstests/tests/generic/701

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/701`. Verify that i_blocks for truncated files larger than 4 GiB have correct values. This test verifies the problem fixed in kernel with commit 92fba084b79e exfat: fix i_blocks for files truncated over 4 GiB It is registered with `_begin_fstest auto`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 50 source line(s).
- Harness registration: `_begin_fstest auto`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_fixed_by_fs_commit exfat 92fba084b79e "exfat: fix i_blocks for files truncated over 4 GiB"`, `_require_test`, `_require_fs_space $TEST_DIR $((5 * 1024 * 1024)) #kB`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `junk_dir=$TEST_DIR/$seq`
- `junk_file=$junk_dir/junk`
- `block_size=`stat -c '%B' $junk_file``
- `iblocks_after_truncate=`stat -c '%b' $junk_file``
- `iblocks_expected=$((4 * 1024 * 1024 * 1024 / $block_size))`

## Control Flow

- Capability gating runs first through `_fixed_by_fs_commit exfat 92fba084b79e "exfat: fix i_blocks for files truncated over 4 GiB"`, `_require_test`, `_require_fs_space $TEST_DIR $((5 * 1024 * 1024)) #kB`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 37: echo "Could not create 5G test file"`
- Key operational lines include:
- `line 42: block_size=`stat -c '%B' $junk_file``
- `line 43: iblocks_after_truncate=`stat -c '%b' $junk_file``

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/701.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_fs_commit exfat 92fba084b79e "exfat: fix i_blocks for files truncated over 4 GiB"`, `_require_test`, `_require_fs_space $TEST_DIR $((5 * 1024 * 1024)) #kB`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 701; Number of allocated blocks after truncate is in range'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
