# sources/test-tools/xfstests/tests/generic/620

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/620`. Since the test is not specific to ext4, hence adding it to generic. Add this test to check for regression which was reported when ext4 bmap aops was moved to use iomap APIs. jbd2 calls bmap() kernel function from fs/inode.c which was failing since iomap_bmap() implementation earlier returned 0 for block addr > INT_MAX. This regression was fixed with following kernel commit commit b75dfde1212 ("fibmap: Warn and return an error in case of block > INT_MAX") It is registered with `_begin_fstest auto mount quick`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 53 source line(s).
- Harness registration: `_begin_fstest auto mount quick`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/dmhugedisk`.
- Capability and skip gates: `_require_scratch_size_nocheck $((4 * 1024 * 1024)) #kB`, `_require_scratch_16T_support`, `_require_dmhugedisk`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `sectors=$((2*1024*1024*1024*17))`
- `chunk_size=128`
- `testfile=$SCRATCH_MNT/testfile-$seq`

## Control Flow

- Capability gating runs first through `_require_scratch_size_nocheck $((4 * 1024 * 1024)) #kB`, `_require_scratch_16T_support`, `_require_dmhugedisk`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- Key operational lines include:
- `line 24: _dmhugedisk_cleanup`
- `line 34: _require_scratch_size_nocheck $((4 * 1024 * 1024)) #kB`
- `line 35: _require_scratch_16T_support`
- `line 36: _require_dmhugedisk`
- `line 43: _dmhugedisk_init $sectors $chunk_size`
- `line 44: _mkfs_dev $DMHUGEDISK_DEV`
- `line 45: _mount $DMHUGEDISK_DEV $SCRATCH_MNT || _fail "mount failed for $DMHUGEDISK_DEV $SCRATCH_MNT"`
- `line 48: $XFS_IO_PROG -fc "pwrite -S 0xaa 0 1m" -c "fsync" $testfile | _filter_xfs_io`
- `line 50: _dmhugedisk_cleanup`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto mount quick`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/dmhugedisk`), and the golden-output file `sources/test-tools/xfstests/tests/generic/620.out` (3 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_size_nocheck $((4 * 1024 * 1024)) #kB`, `_require_scratch_16T_support`, `_require_dmhugedisk`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 3 line(s); its first visible signals are: 'QA output created by 620; wrote 1048576/1048576 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec)'. Runtime pass/fail is also signaled by xfstests output filters. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
