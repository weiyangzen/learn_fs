<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_gdrive.go -->
# sources/sync-backup/kopia/cli/storage_gdrive.go

## Purpose
Implements Google Drive provider flags for extra-provider builds; the provider is noted as not maintained.

## Important APIs, Types, And Functions
Defines `storageGDriveFlags`, `Setup`, `Connect`, and registration. It maps folder ID, read-only, credentials file, embedded credentials, and throttling into `gdrive.Options`.

## Control Flow
Connect optionally reads service account JSON into `ServiceAccountCredentialJSON`, clears the file path, and calls `gdrive.New`.

## State And Persistence Behavior
Persistent repository config can embed credential JSON. Backend object state lives in Google Drive.

## Dependencies And Integration Points
Integrates gdrive blob backend, storage registry, JSON/file helpers, and throttling flags.

## Risks And Edge Cases
Provider maintenance status is a risk. The flag help says `Embed GCS credentials JSON`, which is confusing for GDrive. Embedded credentials require careful config protection.

## Test Signals
Tests should cover registration, required folder ID, embedded credentials, read-only flag, and backend option construction.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_gdrive.go -->
