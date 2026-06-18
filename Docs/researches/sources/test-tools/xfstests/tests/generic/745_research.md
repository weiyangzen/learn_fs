# sources/test-tools/xfstests/tests/generic/745

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/745`. Test that after syncing the filesystem, adding many xattrs to a file, syncing the filesystem again, writing to the file and then doing a fsync against that file, all the xattrs still exists after a power failure. That is, after the fsync log/journal is replayed, the xattrs still exist and with the correct values. This test is motivated by a bug found in btrfs. It is registered with `_begin_fstest auto metadata quick log`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 94 source line(s).
- Harness registration: `_begin_fstest auto metadata quick log`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/dmflakey`, `./common/attr`.
- Capability and skip gates: `_require_scratch`, `_require_dm_target flakey`, `_require_attrs`, `_notrun "Requires support for > 1000 xattrs"`, `_require_metadata_journaling $SCRATCH_DEV`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `num_xattrs=2000`
- `name="user.attr_$(printf "%04d" $i)"`
- `name="user.attr_$(printf "%04d" $i)"`

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_dm_target flakey`, `_require_attrs`, `_notrun "Requires support for > 1000 xattrs"`, `_require_metadata_journaling $SCRATCH_DEV`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 82: echo "File content after crash and log replay:"`
- `line 85: echo "File xattrs after crash and log replay:"`
- `line 88: echo -n "$name="`
- `line 90: echo`
- Key operational lines include:
- `line 21: _cleanup_flakey`
- `line 46: _scratch_mkfs >> $seqres.full 2>&1`
- `line 48: _init_flakey`
- `line 49: _scratch_mount`
- `line 53: $XFS_IO_PROG -f -c "pwrite -S 0xaa 0 32k" $SCRATCH_MNT/foo | _filter_xfs_io`
- `line 54: _scratch_sync`
- `line 69: _scratch_sync`
- `line 76: $XFS_IO_PROG -c "pwrite -S 0xbb 8K 16K" \`
- `line 80: _flakey_drop_and_remount`
- `line 89: _getfattr --absolute-names -n $name --only-values $SCRATCH_MNT/foo`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. Extended attributes are part of the persistent state being created, replayed, or verified. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto metadata quick log`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/dmflakey`, `./common/attr`), and the golden-output file `sources/test-tools/xfstests/tests/generic/745.out` (2014 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_dm_target flakey`, `_require_attrs`, `_notrun "Requires support for > 1000 xattrs"`, `_require_metadata_journaling $SCRATCH_DEV`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.
- The golden output is large, so formatting drift in helper output can create noisy failures even when the core behavior is correct.

## Test Signals

The paired `.out` file has 2014 line(s); its first visible signals are: 'QA output created by 745; wrote 32768/32768 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); wrote 16384/16384 bytes at offset 8192; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec)'. Runtime pass/fail is also signaled by xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
