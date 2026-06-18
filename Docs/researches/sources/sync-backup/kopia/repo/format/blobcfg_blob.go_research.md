# sources/sync-backup/kopia/repo/format/blobcfg_blob.go

## Purpose
Manages the `kopia.blobcfg` blob, which persists blob-storage retention settings separately from the main format blob and encrypts them with the format encryption key.

## Important APIs, Types, And Functions
`KopiaBlobCfgBlobID` names the blob. `BlobStorageConfiguration` stores `RetentionMode` and `RetentionPeriod`. Methods/functions include `IsRetentionEnabled`, `Validate`, `serializeBlobCfgBytes`, `deserializeBlobCfgBytes`, and `KopiaRepositoryJSON.WriteBlobCfgBlob`.

## Control Flow
Validation requires retention mode and period to be provided together and enforces a minimum one-day period. Serialization JSON-marshals the config and either leaves it plaintext for `NONE` or AES-GCM encrypts it for `AES256_GCM`. Deserialization mirrors that path and returns an empty config for nil bytes. Writing encrypts serialized bytes and stores them under `kopia.blobcfg` with retention options applied to the blob write.

## State And Persistence
Persistent state is the `kopia.blobcfg` blob. It may carry retention settings that also affect both blobcfg and repository format blob writes.

## Dependencies And Integration Points
Depends on `blob.Storage`, retention types, `gather`, JSON, and repository format encryption helpers. `format.Manager.Initialize`, `SetParameters`, and `ChangePassword` call this code when creating or rewriting repository configuration.

## Risks And Edge Cases
Bad encryption algorithm names fail serialization/deserialization. Decryption failure is intentionally reported as a generic inability to decrypt blobcfg. Invalid retention values block initialization or parameter updates before partial state should be persisted.

## Test Signals
`format_manager_test.go` covers initialization with retention, retention updates, and invalid negative retention values. Direct serialization corruption is not tested in this subset.
