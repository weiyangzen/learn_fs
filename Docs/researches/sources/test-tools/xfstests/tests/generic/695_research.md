# sources/test-tools/xfstests/tests/generic/695

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/695`. Test that if we punch a hole adjacent to an existing hole, fsync the file and then power fail, the new hole exists after mounting again the filesystem. This is motivated by a regression on btrfs, fixed by the commit mentioned below, when not using the no-holes feature (which is enabled by default since btrfs-progs 5.15). It is registered with `_begin_fstest auto quick log punch fiemap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 90 source line(s).
- Harness registration: `_begin_fstest auto quick log punch fiemap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/dmflakey`, `./common/punch`.
- Capability and skip gates: `_fixed_by_fs_commit btrfs e6e3dec6c3c288 "btrfs: update generation of hole file extent item when merging holes"`, `_require_scratch`, `_require_dm_target flakey`, `_require_xfs_io_command "fpunch"`, `_require_xfs_io_command "fiemap"`, `_require_metadata_journaling $SCRATCH_DEV`, `_require_congruent_file_oplen $SCRATCH_MNT $((2 * 1024 * 1024))`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_fixed_by_fs_commit btrfs e6e3dec6c3c288 "btrfs: update generation of hole file extent item when merging holes"`, `_require_scratch`, `_require_dm_target flakey`, `_require_xfs_io_command "fpunch"`, `_require_xfs_io_command "fiemap"`, plus 2 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 78: echo "File layout after power failure:"`
- `line 83: echo "File content after power failure:"`
- Key operational lines include:
- `line 19: _cleanup_flakey`
- `line 35: _scratch_mkfs >>$seqres.full 2>&1`
- `line 37: _init_flakey`
- `line 38: _scratch_mount`
- `line 49: $XFS_IO_PROG -f -c "truncate 12M" \`
- `line 54: _scratch_sync`
- `line 65: $XFS_IO_PROG -c "fpunch 2M 2M" \`
- `line 71: _flakey_drop_and_remount`
- `line 79: $XFS_IO_PROG -c "fiemap -v" $SCRATCH_MNT/foobar | _filter_fiemap`
- `line 84: _hexdump $SCRATCH_MNT/foobar`
- `line 86: _scratch_unmount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick log punch fiemap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/dmflakey`, `./common/punch`), and the golden-output file `sources/test-tools/xfstests/tests/generic/695.out` (15 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_fs_commit btrfs e6e3dec6c3c288 "btrfs: update generation of hole file extent item when merging holes"`, `_require_scratch`, `_require_dm_target flakey`, `_require_xfs_io_command "fpunch"`, `_require_xfs_io_command "fiemap"`, `_require_metadata_journaling $SCRATCH_DEV`, `_require_congruent_file_oplen $SCRATCH_MNT $((2 * 1024 * 1024))`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.

## Test Signals

The paired `.out` file has 15 line(s); its first visible signals are: 'QA output created by 695; wrote 8388608/8388608 bytes at offset 2097152; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); File layout after power failure:; 0: [0..8191]: hole'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
