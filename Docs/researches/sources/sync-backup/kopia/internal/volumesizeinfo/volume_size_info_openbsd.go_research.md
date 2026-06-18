<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/volumesizeinfo/volume_size_info_openbsd.go -->
# sources/sync-backup/kopia/internal/volumesizeinfo/volume_size_info_openbsd.go

- Purpose: Implements OpenBSD volume size information using OpenBSD statfs field names.
- Important APIs/types/functions: `getPlatformVolumeSizeInfo`.
- Control flow: Calls `unix.Statfs` and computes size/file counts from `F_blocks`, `F_bsize`, `F_bfree`, `F_files`, and `F_ffree`.
- State and persistence: Reads filesystem metadata only.
- Dependencies and integration points: Build-constrained to OpenBSD.
- Risks and edge cases: Separate field names must remain aligned with OpenBSD syscall structs.
- Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/volumesizeinfo/volume_size_info_openbsd.go -->
