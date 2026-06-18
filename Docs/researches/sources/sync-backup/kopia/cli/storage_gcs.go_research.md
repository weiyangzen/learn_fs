<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_gcs.go -->
# sources/sync-backup/kopia/cli/storage_gcs.go

## Purpose
Implements Google Cloud Storage repository provider flags and connection construction.

## Important APIs, Types, And Functions
Defines `storageGCSFlags`, `Setup`, `Connect`, and registration. Options include bucket, prefix, read-only scope, credentials file, embedded credentials, throttling, and point-in-time.

## Control Flow
Setup binds flags and parses point-in-time pre-action. Connect rejects point-in-time on create, optionally reads the service account credentials JSON into config and clears the file path, then calls `gcs.New`.

## State And Persistence Behavior
Persistent repository config may include embedded service account JSON when requested. Otherwise it references a credentials file path. Storage backend state lives in GCS.

## Dependencies And Integration Points
Integrates GCS blob backend, storage provider registry, JSON raw messages, file reads, and throttling flags.

## Risks And Edge Cases
Embedding credentials copies secret JSON into repository config, which has security implications. Point-in-time is read-only. Missing credentials file errors only occur when embedding or backend validates.

## Test Signals
Tests should cover embedding, read-only flag, point-in-time parsing/rejection, and credential file errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_gcs.go -->
