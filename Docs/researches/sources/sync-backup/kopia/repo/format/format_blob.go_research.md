# sources/sync-backup/kopia/repo/format/format_blob.go

## Purpose
Handles the top-level `kopia.repository` JSON blob, format-blob key derivation, encrypted repository config bytes, and recovery of embedded format blobs from packed data.

## Important APIs, Types, And Functions
Defines `KopiaRepositoryJSON`, constants for format encryption/checksum/recovery limits, `KopiaRepositoryBlobID`, `ErrInvalidPassword`, and helpers `ParseKopiaRepositoryJSON`, `DeriveFormatEncryptionKeyFromPassword`, `RecoverFormatBlob`, `recoverFormatBlobWithLength`, `verifyFormatBlobChecksum`, `WriteKopiaRepositoryBlob`, `WriteKopiaRepositoryBlobWithID`, AES-GCM encrypt/decrypt helpers, and `addFormatBlobChecksumAndLength`.

## Control Flow
Parsing JSON unmarshals the repository blob. Password derivation uses repository unique ID and configured KDF. Recovery optionally lists by prefix, reads prefix and suffix chunks, decodes a two-byte length, and validates HMAC-SHA256 checksum with a fixed identifier secret. Writing pretty-prints JSON and stores it with blob retention options. Checksum wrapping returns `<length><data+hmac><length>` so recovery can find it at either file boundary.

## State And Persistence
Persistent state is `kopia.repository`, which contains public metadata, unique ID, KDF name, format encryption algorithm, and encrypted repository configuration bytes. Recovery helpers operate on copies embedded elsewhere, such as format bytes stored inside pack data.

## Dependencies And Integration Points
Depends on `internal/crypto`, `blob.Storage`, `gather`, JSON, HMAC/SHA256, and retention-aware blob writes. The format manager calls these functions for initialization, refresh, password changes, and upgrades.

## Risks And Edge Cases
Invalid password is surfaced by callers after decrypt failure. Recovery only reads up to 64 KiB from each end and caps checksummed format bytes at 65,000 bytes. `decodeInt16` assumes at least two bytes; callers guard chunk lengths before use. The checksum secret identifies format blocks but is not intended to be secret.

## Test Signals
`format_blob_test.go` covers recovery from standalone, prefix, and suffix positions plus bad checksums, missing blobs, and too-short blobs.
