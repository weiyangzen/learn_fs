# sources/test-tools/xfstests/tests/generic/742

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/742`. Test fiemap into an mmaped buffer of the same file Create a reasonably large file, then run a program which mmaps it and uses that as a buffer for an fiemap call. This is a regression test for btrfs where we used to hold a lock for the duration of the fiemap call which would result in a deadlock if we page faulted. It is registered with `_begin_fstest quick auto fiemap mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 49 source line(s).
- Harness registration: `_begin_fstest quick auto fiemap mmap`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_fixed_by_fs_commit btrfs b0ad381fa769 "btrfs: fix deadlock with fiemap and extent locking"`, `_require_test`, `_require_test_program "fiemap-fault"`, `_require_test_program "punch-alternating"`, `_require_xfs_io_command "fpunch"`, `_require_xfs_io_command "fiemap"`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: `$here/src/punch-alternating $dst`, `$here/src/fiemap-fault $dst`.
- Notable variables and constants:
- `dst=$TEST_DIR/$seq/fiemap-fault`
- `blksz=$(_get_file_block_size $TEST_DIR)`

## Control Flow

- Capability gating runs first through `_fixed_by_fs_commit btrfs b0ad381fa769 "btrfs: fix deadlock with fiemap and extent locking"`, `_require_test`, `_require_test_program "fiemap-fault"`, `_require_test_program "punch-alternating"`, `_require_xfs_io_command "fpunch"`, plus 1 more.
- User-visible phase markers include:
- `line 37: echo "Silence is golden"`
- Key operational lines include:
- `line 15: _begin_fstest quick auto fiemap mmap`
- `line 41: $XFS_IO_PROG -f -c "pwrite -q 0 $((blksz * 10000))" $dst`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest quick auto fiemap mmap`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/742.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_fs_commit btrfs b0ad381fa769 "btrfs: fix deadlock with fiemap and extent locking"`, `_require_test`, `_require_test_program "fiemap-fault"`, `_require_test_program "punch-alternating"`, `_require_xfs_io_command "fpunch"`, `_require_xfs_io_command "fiemap"`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 742; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
