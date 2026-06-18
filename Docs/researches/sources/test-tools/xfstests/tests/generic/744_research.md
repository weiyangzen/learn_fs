# sources/test-tools/xfstests/tests/generic/744

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/744`. Set up a filesystem, create a clone, mount both, and verify if the cp reflink operation between these two mounts fails. It is registered with `_begin_fstest auto clone volume tempfsid`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 80 source line(s).
- Harness registration: `_begin_fstest auto clone volume tempfsid`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_duplicate_fsid`, `_require_test`, `_require_block_device $TEST_DEV`, `_require_test_reflink`, `_require_cp_reflink`, `_require_loop`.
- Local shell functions: `_cleanup`, `clone_filesystem`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `mnt1=$TEST_DIR/$seq/mnt1`
- `mnt2=$TEST_DIR/$seq/mnt2`
- `loop_file1="$TEST_DIR/$seq/image1"`
- `loop_dev1=$(_create_loop_device "$loop_file1")`
- `loop_file2="$TEST_DIR/$seq/image2"`
- `loop_dev2=$(_create_loop_device "$loop_file2")`

## Control Flow

- Capability gating runs first through `_require_duplicate_fsid`, `_require_test`, `_require_block_device $TEST_DEV`, `_require_test_reflink`, `_require_cp_reflink`, plus 1 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- Key operational lines include:
- `line 18: _unmount $mnt2 &> /dev/null`
- `line 19: _unmount $mnt1 &> /dev/null`
- `line 20: [ -b "$loop_dev2" ] && _destroy_loop_device $loop_dev2`
- `line 21: [ -b "$loop_dev1" ] && _destroy_loop_device $loop_dev1`
- `line 32: _require_test_reflink`
- `line 33: _require_cp_reflink`
- `line 41: _mkfs_dev $dev1`
- `line 43: _mount $dev1 $mnt1`
- `line 44: $XFS_IO_PROG -fc 'pwrite -S 0x61 0 9000' $mnt1/foo >> $seqres.full`
- `line 45: _unmount $mnt1`
- `line 60: loop_dev1=$(_create_loop_device "$loop_file1")`
- `line 64: loop_dev2=$(_create_loop_device "$loop_file2")`
- `line 69: _mount $loop_dev1 $mnt1`
- `line 70: $XFS_IO_PROG -fc 'pwrite -S 0x61 0 9000' $mnt1/foo | _filter_xfs_io`
- `line 73: _mount $loop_dev2 $mnt2 || _fail "mount of cloned device failed"`
- `line 76: _cp_reflink $mnt1/foo $mnt2/bar 2>&1 | _filter_test_dir`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto clone volume tempfsid`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/744.out` (4 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_duplicate_fsid`, `_require_test`, `_require_block_device $TEST_DEV`, `_require_test_reflink`, `_require_cp_reflink`, `_require_loop`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 4 line(s); its first visible signals are: "QA output created by 744; wrote 9000/9000 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); cp: failed to clone 'TEST_DIR/744/mnt2/bar' from 'TEST_DIR/744/mnt1/foo': Invalid cross-device link". Runtime pass/fail is also signaled by xfstests output filters, hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
