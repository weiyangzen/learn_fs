# sources/test-tools/xfstests/tests/generic/675

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/675`. Functional test for dropping suid and sgid capabilities as part of a reflink. It is registered with `_begin_fstest auto clone quick`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 71 source line(s).
- Harness registration: `_begin_fstest auto clone quick`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`, `./common/attr`.
- Capability and skip gates: `_require_user`, `_require_command "$GETCAP_PROG" getcap`, `_require_command "$SETCAP_PROG" setcap`, `_require_scratch_reflink`, `_require_attrs security`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576`.
- Local shell functions: `setup_testfile`, `commit_and_check`.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_require_user`, `_require_command "$GETCAP_PROG" getcap`, `_require_command "$SETCAP_PROG" setcap`, `_require_scratch_reflink`, `_require_attrs security`, plus 1 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 56: echo`
- `line 60: echo "Test 1 - qa_user"`
- `line 65: echo "Test 2 - root"`
- Key operational lines include:
- `line 22: _require_scratch_reflink`
- `line 25: _scratch_mkfs >> $seqres.full`
- `line 26: _scratch_mount`
- `line 36: _scratch_sync`
- `line 42: stat -c '%a %A %n' $SCRATCH_MNT/a | _filter_scratch`
- `line 45: local cmd="$XFS_IO_PROG -c 'reflink $SCRATCH_MNT/b 0 0 1m' $SCRATCH_MNT/a"`
- `line 52: stat -c '%a %A %n' $SCRATCH_MNT/a | _filter_scratch`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Extended attributes are part of the persistent state being created, replayed, or verified. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto clone quick`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`, `./common/attr`), and the golden-output file `sources/test-tools/xfstests/tests/generic/675.out` (13 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_user`, `_require_command "$GETCAP_PROG" getcap`, `_require_command "$SETCAP_PROG" setcap`, `_require_scratch_reflink`, `_require_attrs security`, `_require_congruent_file_oplen $SCRATCH_MNT 1048576`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 13 line(s); its first visible signals are: 'QA output created by 675; Test 1 - qa_user; 777 -rwxrwxrwx SCRATCH_MNT/a; SCRATCH_MNT/a cap_setgid,cap_setuid=ep; 777 -rwxrwxrwx SCRATCH_MNT/a'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
