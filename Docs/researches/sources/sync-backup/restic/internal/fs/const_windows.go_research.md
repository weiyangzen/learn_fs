# sources/sync-backup/restic/internal/fs/const_windows.go

Purpose: Provides Windows-safe definitions for flags used by the filesystem abstraction.

Important APIs: Invented internal `O_NOFOLLOW`, no-op `O_DIRECTORY`, and `sanitizeFlags`.

Control flow and state: `sanitizeFlags` removes the package-local `O_NOFOLLOW` bit before passing flags to Go/Windows file APIs. `O_DIRECTORY` is zero because Windows directory access is handled elsewhere.

Dependencies and integration: Lets common code compile and call `OpenFile` with Unix-like flags. Metadata-only handling in `localFile.cacheFI` interprets `O_NOFOLLOW`.

Risks: Comments note Windows `OpenFile` does not fully honor all flags. The invented flag must not leak into external APIs, hence the final sanitization step.

Test signals: Windows local metadata tests rely on symlink-follow decisions; Windows temp file and VSS tests indirectly depend on flag sanitization.
