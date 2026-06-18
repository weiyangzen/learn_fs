# sources/test-tools/xfstests/tests/generic/702

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/702`. Test that if we have two consecutive extents and only one of them is cloned, then fiemap correctly reports which one is shared and reports the other as not shared. It is registered with `_begin_fstest auto quick clone fiemap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 91 source line(s).
- Harness registration: `_begin_fstest auto quick clone fiemap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_fixed_by_fs_commit btrfs ac3c0d36a2a2f7 "btrfs: make fiemap more efficient and accurate reporting extent sharedness"`, `_require_scratch_reflink`, `_require_xfs_io_command "fiemap"`, `_require_congruent_file_oplen $SCRATCH_MNT $((128 * 1024))`.
- Local shell functions: `fiemap_test_file`.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_fixed_by_fs_commit btrfs ac3c0d36a2a2f7 "btrfs: make fiemap more efficient and accurate reporting extent sharedness"`, `_require_scratch_reflink`, `_require_xfs_io_command "fiemap"`, `_require_congruent_file_oplen $SCRATCH_MNT $((128 * 1024))`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- User-visible phase markers include:
- `line 55: echo "Creating file foo"`
- `line 61: echo "Cloning first extent of file foo to file bar"`
- `line 67: echo "fiemap of file foo:"`
- `line 74: echo "Creating file foo2"`
- `line 80: echo "Cloning second extent of file foo2 to file bar2"`
- `line 86: echo "fiemap of file foo2:"`
- Key operational lines include:
- `line 20: _require_scratch_reflink`
- `line 43: $XFS_IO_PROG -c "fiemap -v" $filepath | tail -n +3 | \`
- `line 48: _scratch_mkfs >> $seqres.full`
- `line 49: _scratch_mount`
- `line 56: $XFS_IO_PROG -f -c "pwrite -b 128K 0 128K" -c "fsync" \`
- `line 62: $XFS_IO_PROG -f -c "reflink $SCRATCH_MNT/foo 0 0 128K" $SCRATCH_MNT/bar | \`
- `line 75: $XFS_IO_PROG -f -c "pwrite -b 128K 0 128K" -c "fsync" \`
- `line 81: $XFS_IO_PROG -f -c "reflink $SCRATCH_MNT/foo2 128K 0 128K" $SCRATCH_MNT/bar2 | \`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick clone fiemap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/702.out` (23 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_fs_commit btrfs ac3c0d36a2a2f7 "btrfs: make fiemap more efficient and accurate reporting extent sharedness"`, `_require_scratch_reflink`, `_require_xfs_io_command "fiemap"`, `_require_congruent_file_oplen $SCRATCH_MNT $((128 * 1024))`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 23 line(s); its first visible signals are: 'QA output created by 702; Creating file foo; wrote 131072/131072 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); wrote 131072/131072 bytes at offset 131072'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
