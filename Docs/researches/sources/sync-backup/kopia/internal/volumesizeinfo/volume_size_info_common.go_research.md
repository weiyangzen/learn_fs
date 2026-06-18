<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/volumesizeinfo/volume_size_info_common.go -->
# sources/sync-backup/kopia/internal/volumesizeinfo/volume_size_info_common.go

- Purpose: Implements volume size information for non-OpenBSD, non-Windows Unix platforms.
- Important APIs/types/functions: `getPlatformVolumeSizeInfo`.
- Control flow: Calls `unix.Statfs`, computes total bytes, used bytes, and used file count from block/file counters.
- State and persistence: Reads filesystem metadata only.
- Dependencies and integration points: Build-constrained to `!openbsd && !windows`; uses `x/sys/unix`.
- Risks and edge cases: Uses unsigned arithmetic on statfs counters; unusual filesystems may report unexpected values.
- Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/volumesizeinfo/volume_size_info_common.go -->
