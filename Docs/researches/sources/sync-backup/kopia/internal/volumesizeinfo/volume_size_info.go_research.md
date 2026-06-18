<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/volumesizeinfo/volume_size_info.go -->
# sources/sync-backup/kopia/internal/volumesizeinfo/volume_size_info.go

- Purpose: Exposes cross-platform volume size information API.
- Important APIs/types/functions: `VolumeSizeInfo`, `GetVolumeSizeInfo`.
- Control flow: Validates non-empty mount point, delegates to platform implementation, and wraps errors with mount point context.
- State and persistence: Reads filesystem/volume metadata only.
- Dependencies and integration points: Used by storage/capacity reporting code; delegates to build-tagged platform files.
- Risks and edge cases: File count semantics are platform-dependent, especially Windows.
- Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/volumesizeinfo/volume_size_info.go -->
