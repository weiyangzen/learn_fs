# sources/test-tools/xfstests/tests/generic/367

## Purpose
This test verifies that extent allocation hint setting works correctly on files with no extents allocated and non-empty files which are truncated. It also checks that the extent hints setting fails with non-empty file i.e, with any file with allocated extents or delayed allocation. We also check if the extsize value and the xflag bit actually got reflected after setting/re-setting the extsize value. It is registered as generic/367 with `_begin_fstest` tags `ioctl, quick`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: get_default_extsize, filter_extsz, setup, read_file_extsize, check_extsz_and_xflag, check_extsz_xflag_across_remount, reset_extsz_and_recheck_extsz_xflag, check_extsz_xflag_before_and_after_reset, test_empty_file, test_data_delayed, test_data_allocated, test_truncate_allocated, test_truncate_delayed. Important state variables and paths include FILE_DATA_SIZE=1M, NEW_FILE_NAME_PREFIX=$SCRATCH_MNT/new-file-. Topic focus: general filesystem semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; remounts or replays after simulated failure; wraps repeated scenarios in local helper functions get_default_extsize, filter_extsz, setup, read_file_extsize, check_extsz_and_xflag, check_extsz_xflag_across_remount.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch_extsize.

Documented regression fixes: _fixed_by_fs_commit xfs 2a492ff66673 "xfs: Check for delayed allocations before setting extsize".

External/helper commands: $XFS_IO_PROG, mount, sed, truncate.

Representative `xfs_io` operations: extsize; extsize 0; open -f $filename; extsize $EXTSIZE; pwrite -q  0 $FILE_DATA_SIZE; pwrite -qW  0 $FILE_DATA_SIZE; truncate 0.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: TEST: Set extsize on empty file; [EXTSIZE] SCRATCH_MNT/new-file-00; e flag set; Re-setting extsize hint to 0; [EXTSIZE] SCRATCH_MNT/new-file-00; e flag unset. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
