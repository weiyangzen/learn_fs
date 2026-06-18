# sources/test-tools/xfstests/tests/btrfs/292

## Purpose
Test btrfs behavior with large chunks (size beyond 4G) for basic read-write and discard. This test focus on RAID0. Make sure each device has at least 2G. Btrfs has a limits on per-device stripe length of 1G. Double that so that we can ensure a RAID0 data chunk with 6G size. We disable async/sync auto discard, so that btrfs won't try to cache the discard result which can cause unexpected skip for some trim range. Fill the data chunk with 5G data. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, discard/trim behavior.

## Important APIs, Types, and Functions
The fstest declaration is `auto raid volume trim`. Requirement and capability gates: line 16: `_require_scratch_dev_pool 6`; line 17: `_require_fstrim`; line 43: `_require_batched_discard $SCRATCH_MNT`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 16: `_require_scratch_dev_pool 6`; line 17: `_require_fstrim`; line 21: `_scratch_dev_pool_get 6`; line 33: `_scratch_dev_pool_put`; line 34: `_notrun "device $i is too small, need at least 2G"`; line 38: `_scratch_pool_mkfs -m raid1 -d raid0 >> $seqres.full 2>&1`; line 42: `_scratch_mount -o nodiscard`; line 43: `_require_batched_discard $SCRATCH_MNT`; line 47: `$XFS_IO_PROG -f -c "pwrite -i /dev/urandom 0 $filesize" $SCRATCH_MNT/file_$i > /dev/null`; line 50: `sync`; line 52: `$BTRFS_UTIL_PROG filesystem df $SCRATCH_MNT >> $seqres.full`; line 54: `_scratch_unmount`; line 57: `$BTRFS_UTIL_PROG check --check-data-csum $SCRATCH_DEV >> $seqres.full 2>&1`; line 65: `rm -rf - "$SCRATCH_MNT/*[02468]"`. It documents fixed kernel commit context at line 18: `_fixed_by_kernel_commit a7299a18a179 \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto raid volume trim`, install cleanup if needed, enforce requirements, then mounts the test filesystem, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io, fstrim/discard support. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 292 | Silence is golden`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools; discard tests are sensitive to block-device discard support and whether allocated extents are accidentally punched on replacement devices. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
