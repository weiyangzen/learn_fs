# sources/sync-backup/kopia/repo/blob/filesystem/filesystem_storage_capacity_windows.go

Purpose: Windows-specific capacity reporting for filesystem storage.

Important APIs/types/functions: `(*fsStorage).GetCapacity`, implemented with Windows disk-free-space APIs.

Control flow: the method queries capacity for the storage path and converts Windows values into Kopia's `blob.Capacity` result.

State and persistence behavior: read-only capacity query; no files are created or modified.

Dependencies/integration points: selected only on Windows builds and used by generic capacity reporting. Risks include path normalization/long-path behavior, drive/share reporting differences, and platform-specific API failures. Test coverage is likely indirect through Windows CI/shared filesystem storage tests rather than dedicated unit tests in this subset.
