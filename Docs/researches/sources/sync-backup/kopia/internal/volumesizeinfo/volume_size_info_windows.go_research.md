<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/volumesizeinfo/volume_size_info_windows.go -->
# sources/sync-backup/kopia/internal/volumesizeinfo/volume_size_info_windows.go

- Purpose: Implements Windows volume size information using `GetDiskFreeSpaceEx`.
- Important APIs/types/functions: `getPlatformVolumeSizeInfo`.
- Control flow: Converts mount point to UTF-16, fills capacity/free fields, returns total, used, and `math.MaxInt64` as a sentinel file count.
- State and persistence: Reads volume metadata only.
- Dependencies and integration points: Build-constrained to Windows; uses `x/sys/windows` and `repo/blob.Capacity`.
- Risks and edge cases: File count is not measurable and should not be treated as exact.
- Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/volumesizeinfo/volume_size_info_windows.go -->
