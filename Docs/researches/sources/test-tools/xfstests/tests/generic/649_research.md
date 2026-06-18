# sources/test-tools/xfstests/tests/generic/649

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/649`. Regression test for commit: 72a048c1056a ("xfs: only set IOMAP_F_SHARED when providing a srcmap to a write") If a user creates a sparse shared region in a file, convinces XFS to create a copy-on-write delayed allocation reservation spanning both the shared blocks and the holes, and then calls the fallocate unshare command to unshare the entire sparse region, XFS incorrectly tells iomap that the delalloc blocks for the holes are shared, which causes it to error out while trying to unshare a hole. It is registered with `_begin_fstest auto clone unshare punch`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 78 source line(s).
- Harness registration: `_begin_fstest auto clone unshare punch`.
- Imported common libraries: `./common/preamble`, `./common/reflink`, `./common/filter`.
- Capability and skip gates: `_fixed_by_fs_commit xfs 72a048c1056a "xfs: only set IOMAP_F_SHARED when providing a srcmap to a write"`, `_require_cp_reflink`, `_require_test_reflink`, `_require_test_program "punch-alternating"`, `_require_xfs_io_command "fpunch"	# make sure punch-alt can do its job`, `_require_xfs_io_command "funshare"`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: `$here/src/punch-alternating -o 1 $file2`.
- Notable variables and constants:
- `file1=$TEST_DIR/$seq/a`
- `file2=$TEST_DIR/$seq/b`
- `f1sum0="$(md5sum $file1 | _filter_test_dir)"`
- `f2sum0="$(md5sum $file2 | _filter_test_dir)"`
- `f1sum1="$(md5sum $file1 | _filter_test_dir)"`
- `f2sum1="$(md5sum $file2 | _filter_test_dir)"`
- `f1sum2="$(md5sum $file1 | _filter_test_dir)"`
- `f2sum2="$(md5sum $file2 | _filter_test_dir)"`

## Control Flow

- Capability gating runs first through `_fixed_by_fs_commit xfs 72a048c1056a "xfs: only set IOMAP_F_SHARED when providing a srcmap to a write"`, `_require_cp_reflink`, `_require_test_reflink`, `_require_test_program "punch-alternating"`, `_require_xfs_io_command "fpunch"	# make sure punch-alt can do its job`, plus 1 more.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 76: echo Silence is golden`
- Key operational lines include:
- `line 37: _require_cp_reflink`
- `line 38: _require_test_reflink`
- `line 48: $XFS_IO_PROG -f -c "pwrite -S 0x58 -b 10m 0 10m" $file1 >> $seqres.full`
- `line 50: f1sum0="$(md5sum $file1 | _filter_test_dir)"`
- `line 52: _cp_reflink $file1 $file2`
- `line 55: f2sum0="$(md5sum $file2 | _filter_test_dir)"`
- `line 58: test "$FSTYP" = "xfs" && $XFS_IO_PROG -c 'cowextsize 0' $file2`
- `line 59: $XFS_IO_PROG -c "funshare 0 10m" $file2`
- `line 61: f1sum1="$(md5sum $file1 | _filter_test_dir)"`
- `line 62: f2sum1="$(md5sum $file2 | _filter_test_dir)"`
- `line 69: f1sum2="$(md5sum $file1 | _filter_test_dir)"`
- `line 70: f2sum2="$(md5sum $file2 | _filter_test_dir)"`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto clone unshare punch`, common helper libraries (`./common/preamble`, `./common/reflink`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/649.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_fs_commit xfs 72a048c1056a "xfs: only set IOMAP_F_SHARED when providing a srcmap to a write"`, `_require_cp_reflink`, `_require_test_reflink`, `_require_test_program "punch-alternating"`, `_require_xfs_io_command "fpunch"	# make sure punch-alt can do its job`, `_require_xfs_io_command "funshare"`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 649; Silence is golden'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
