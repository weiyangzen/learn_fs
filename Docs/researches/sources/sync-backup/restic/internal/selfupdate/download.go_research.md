<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/selfupdate/download.go -->
# sources/sync-backup/restic/internal/selfupdate/download.go

## Purpose
Implements the high-level self-update download, verification, hash checking, archive extraction, and atomic replacement path.

## Important APIs and Control Flow
`findHash`, `extractToFile`, and `DownloadLatestStableRelease` are central. The update flow fetches GitHub latest release metadata, skips if already current, downloads `SHA256SUMS` and its signature, verifies the signature, downloads the platform archive, checks its SHA256, extracts bz2/zip content to a temp file, removes or renames the old binary, atomically renames the new file, and preserves executable mode. Errors abort at every verification or filesystem step. `extractToFile` handles zip archives with exactly one member and bz2/plain data.

## State, Persistence, Dependencies, and Integration
Persistent state is the replaced restic binary and a temporary file in the target directory. Dependencies include GitHub asset helpers, embedded GPG verification, archive readers, SHA256, and platform-specific `removeResticBinary`.

## Risks and Test Signals
Risks are supply-chain critical: signature/hash verification must stay mandatory, zip member assumptions must hold, and binary replacement must be atomic. Tests cover zip extraction and overwrite behavior; GitHub request tests cover auth headers.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/selfupdate/download.go -->
