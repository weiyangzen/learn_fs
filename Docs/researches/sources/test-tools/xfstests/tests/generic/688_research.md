# sources/test-tools/xfstests/tests/generic/688

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/688`. Functional test for dropping capability bits as part of an fallocate. It is registered with `_begin_fstest auto prealloc quick`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 78 source line(s).
- Harness registration: `_begin_fstest auto prealloc quick`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/attr`.
- Capability and skip gates: `_require_user`, `_require_command "$GETCAP_PROG" getcap`, `_require_command "$SETCAP_PROG" setcap`, `_require_xfs_io_command falloc`, `_require_test`, `_require_congruent_file_oplen $TEST_DIR 65536`, `_require_attrs security`.
- Local shell functions: `_cleanup`, `setup_testfile`, `commit_and_check`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `junk_dir=$TEST_DIR/$seq`
- `junk_file=$junk_dir/a`

## Control Flow

- Capability gating runs first through `_require_user`, `_require_command "$GETCAP_PROG" getcap`, `_require_command "$SETCAP_PROG" setcap`, `_require_xfs_io_command falloc`, `_require_test`, plus 2 more.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 63: echo`
- `line 67: echo "Test 1 - qa_user"`
- `line 72: echo "Test 2 - root"`
- Key operational lines include:
- `line 28: _require_xfs_io_command falloc`
- `line 49: stat -c '%a %A %n' $junk_file | _filter_test_dir`
- `line 52: local cmd="$XFS_IO_PROG -c 'falloc 0 64k' $junk_file"`
- `line 59: stat -c '%a %A %n' $junk_file | _filter_test_dir`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Extended attributes are part of the persistent state being created, replayed, or verified. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto prealloc quick`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/attr`), and the golden-output file `sources/test-tools/xfstests/tests/generic/688.out` (13 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_user`, `_require_command "$GETCAP_PROG" getcap`, `_require_command "$SETCAP_PROG" setcap`, `_require_xfs_io_command falloc`, `_require_test`, `_require_congruent_file_oplen $TEST_DIR 65536`, `_require_attrs security`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 13 line(s); its first visible signals are: 'QA output created by 688; Test 1 - qa_user; 777 -rwxrwxrwx TEST_DIR/688/a; TEST_DIR/688/a cap_setgid,cap_setuid=ep; 777 -rwxrwxrwx TEST_DIR/688/a'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
