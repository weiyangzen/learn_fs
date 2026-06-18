# sources/test-tools/xfstests/tests/generic/684

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/684`. Functional test for dropping suid and sgid bits as part of a fpunch. It is registered with `_begin_fstest auto clone quick perms punch`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 125 source line(s).
- Harness registration: `_begin_fstest auto clone quick perms punch`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_user`, `_require_test`, `_require_xfs_io_command $verb`, `_require_congruent_file_oplen $TEST_DIR 65536`.
- Local shell functions: `_cleanup`, `setup_testfile`, `commit_and_check`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `verb=fpunch`
- `junk_dir=$TEST_DIR/$seq`
- `junk_file=$junk_dir/a`

## Control Flow

- Capability gating runs first through `_require_user`, `_require_test`, `_require_xfs_io_command $verb`, `_require_congruent_file_oplen $TEST_DIR 65536`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 60: echo`
- `line 64: echo "Test 1 - qa_user, non-exec file $verb"`
- `line 70: echo "Test 2 - qa_user, group-exec file $verb"`
- `line 76: echo "Test 3 - qa_user, user-exec file $verb"`
- `line 82: echo "Test 4 - qa_user, all-exec file $verb"`
- `line 88: echo "Test 5 - root, non-exec file $verb"`
- `line 94: echo "Test 6 - root, group-exec file $verb"`
- `line 100: echo "Test 7 - root, user-exec file $verb"`
- Key operational lines include:
- `line 48: stat -c '%a %A %n' $junk_file | _filter_test_dir`
- `line 50: local cmd="$XFS_IO_PROG -c '$command $start $end' $junk_file"`
- `line 57: stat -c '%a %A %n' $junk_file | _filter_test_dir`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto clone quick perms punch`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/684.out` (41 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_user`, `_require_test`, `_require_xfs_io_command $verb`, `_require_congruent_file_oplen $TEST_DIR 65536`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 41 line(s); its first visible signals are: 'QA output created by 684; Test 1 - qa_user, non-exec file fpunch; 6666 -rwSrwSrw- TEST_DIR/684/a; 666 -rw-rw-rw- TEST_DIR/684/a'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
