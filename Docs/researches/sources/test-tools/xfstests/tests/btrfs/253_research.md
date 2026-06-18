# sources/test-tools/xfstests/tests/btrfs/253

## Purpose
Test the new /sys/fs/btrfs/<uuid>/allocation/<block-type>/chunk_size setting. This setting allows the admin to change the chunk size setting for the next allocation. Test 1: Allocate storage for all three block types (data, metadata and system) with the default chunk size. Test 2: Set a new chunk size to double the default size and allocate space for all new block types with the new chunk size. In this subset it primarily covers Btrfs filesystem behavior through xfstests shell orchestration.

## Important APIs, Types, and Functions
The fstest declaration is `auto`. Requirement and capability gates: line 79: `_require_test`; line 80: `_require_scratch`; line 82: `_require_non_zoned_device "$SCRATCH_DEV"`; line 93: `_require_fs_sysfs allocation/metadata/chunk_size`; line 94: `_require_fs_sysfs allocation/metadata/force_chunk_alloc`. Local helper surface: `parse_size_string()` (line 37), `device_size()` (line 47), `free_space()` (line 59), `alloc_size()` (line 72). Important command/API calls include line 47: `device_size() {`; line 79: `_require_test`; line 80: `_require_scratch`; line 82: `_require_non_zoned_device "$SCRATCH_DEV"`; line 85: `rm -f "${seqres}.full"`; line 89: `_scratch_mkfs_sized $((10 * 1024 * 1024 * 1024)) >> $seqres.full 2>&1`; line 90: `_scratch_mount >> $seqres.full 2>&1`; line 93: `_require_fs_sysfs allocation/metadata/chunk_size`; line 94: `_require_fs_sysfs allocation/metadata/force_chunk_alloc`; line 98: `device_size DEVICE_SIZE_MB`; line 202: `_fail "Cannot find allocation size for partial block allocation."`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through standard xfstests common helpers and btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 253 | Capture default chunk sizes. | First allocation. | Second allocation. | Calculate request size so last memory allocation cannot be completely fullfilled. | Third allocation. | Force allocation of system block type must fail. | No space left on device | ... (11 expected-output lines total)`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
