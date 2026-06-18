# sources/test-tools/xfstests/tests/generic/746

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/746`. Test that filesystem sends discard requests only on free blocks It is registered with `_begin_fstest auto trim fiemap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 247 source line(s).
- Harness registration: `_begin_fstest auto trim fiemap`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_require_test`, `_require_loop`, `_require_fstrim`, `_require_xfs_io_command "fiemap"`, `_require_fs_space $TEST_DIR 307200`, `_require_btrfs_command inspect-internal dump-super`, `_require_btrfs_command inspect-internal dump-tree`, `_require_fs_space $TEST_DIR 3145728`, `_require_dumpe2fs`, `_notrun "Requires fs-specific way to check discard ranges"`, plus 1 more.
- Local shell functions: `_cleanup`, `get_holes`, `get_free_sectors`, `merge_ranges`.
- External `$here/src` helpers: `$PYTHON3_PROG $here/src/parse-free-space.py -n $nodesize -b $tmp/bg_dump \`, `-f $here/src/parse-dev-tree.awk >> $tmp/unallocated`.
- Notable variables and constants:
- `fssize=$(_small_fs_size_mb 300) # 200m phys/virt size`
- `fssize=3000`
- `agsize=`$XFS_INFO_PROG $loop_mnt | $SED_PROG -n 's/.*agsize=\(.*\) blks.*/\1/p'``
- `file1=$1`
- `file2=$2`
- `tmp_file=$tmp/sectors.tmp`
- `start=${line% *}`
- `end=${line#* }`
- `curr_start=${line% *}`
- `curr_end=${line#* }`
- `end=$curr_end`
- `start=$curr_start`

## Control Flow

- Capability gating runs first through `_require_test`, `_require_loop`, `_require_fstrim`, `_require_xfs_io_command "fiemap"`, `_require_fs_space $TEST_DIR 307200`, plus 6 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 142: echo $start $end`
- `line 149: echo $start $end`
- `line 181: echo -n "Generating garbage on loop..."`
- `line 195: echo "done."`
- `line 197: echo -n "Running fstrim..."`
- `line 199: echo "done."`
- `line 201: echo -n "Detecting interesting holes in image..."`
- `line 205: echo "done."`
- Key operational lines include:
- `line 14: _require_fstrim`
- `line 41: _unmount $loop_mnt &> /dev/null`
- `line 42: [ -n "$loop_dev" ] && _destroy_loop_device $loop_dev`
- `line 56: _unmount $loop_mnt`
- `line 60: $XFS_IO_PROG -F -c fiemap $img_file | grep hole | \`
- `line 62: _mount $loop_dev $loop_mnt`
- `line 69: _unmount $loop_mnt`
- `line 70: $DUMPE2FS_PROG $loop_dev 2>&1 | grep " Free blocks" | cut -d ":" -f2- | \`
- `line 83: _unmount $loop_mnt`
- `line 84: $XFS_DB_PROG -r -c "freesp -d" $loop_dev | $SED_PROG '/^.*from/,$d'| \`
- `line 89: local device_size=$($BTRFS_UTIL_PROG filesystem show --raw $loop_mnt 2>&1 \`
- `line 92: local nodesize=$($BTRFS_UTIL_PROG inspect-internal dump-super $loop_dev \`
- `line 96: $BTRFS_UTIL_PROG inspect-internal dump-tree -t extent $loop_dev >> $tmp/extent_dump`
- `line 97: if $BTRFS_UTIL_PROG inspect-internal dump-super $loop_dev |\`
- `line 99: $BTRFS_UTIL_PROG inspect-internal dump-tree -t block-group $loop_dev \`
- `line 108: $BTRFS_UTIL_PROG inspect-internal dump-tree -t dev $loop_dev \`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto trim fiemap`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/746.out` (5 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_loop`, `_require_fstrim`, `_require_xfs_io_command "fiemap"`, `_require_fs_space $TEST_DIR 307200`, `_require_btrfs_command inspect-internal dump-super`, `_require_btrfs_command inspect-internal dump-tree`, `_require_fs_space $TEST_DIR 3145728`, plus 3 more.

## Risks and Edge Cases

- Discard/free-space validation is sensitive to filesystem-specific layout tools and block-to-sector conversion assumptions.

## Test Signals

The paired `.out` file has 5 line(s); its first visible signals are: 'QA output created by 746; Generating garbage on loop...done.; Running fstrim...done.; Detecting interesting holes in image...done.; Comparing holes to the reported space from FS...done.'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
