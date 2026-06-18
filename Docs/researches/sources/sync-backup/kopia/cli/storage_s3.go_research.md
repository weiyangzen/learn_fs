<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_s3.go -->
# sources/sync-backup/kopia/cli/storage_s3.go

## Purpose
Implements S3 repository provider flags, including TLS options, custom root CA input, credentials, prefix, endpoint, region, throttling, and point-in-time reads.

## Important APIs, Types, And Functions
Key symbols are `storageS3Flags`, `Setup`, `preActionLoadPEMPath`, `preActionLoadPEMBase64`, `Connect`, and registration.

## Control Flow
Setup binds required bucket/access/secret flags and optional session token, prefix, TLS controls, point-in-time pre-action, and root CA pre-actions. Connect rejects point-in-time for repository creation and calls `s3.New`.

## State And Persistence Behavior
Persistent config can include credentials, TLS verification choices, custom CA bytes, and point-in-time read settings. Backend object state lives in S3-compatible storage.

## Dependencies And Integration Points
Integrates S3 blob backend, storage registry, env-name namespacing, base64 decoding, file reads, throttling, and Kingpin pre-actions.

## Risks And Edge Cases
`--disable-tls-verification` and `--disable-tls` are security-sensitive. `preActionLoadPEMBase64` accepts empty base64 and sets RootCA to empty. Mutual exclusion is enforced only when path pre-action sees RootCA already set.

## Test Signals
Tests cover root CA base64/path loading and mutual exclusion. Additional tests should cover point-in-time create rejection and TLS flag propagation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_s3.go -->
