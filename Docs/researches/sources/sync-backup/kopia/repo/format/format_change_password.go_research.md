# sources/sync-backup/kopia/repo/format/format_change_password.go

## Purpose
Re-encrypts repository format and blob storage configuration with a new password-derived format encryption key.

## Important APIs, Types, And Functions
`Manager.ChangePassword(ctx, newPassword)` is the sole function.

## Control Flow
The manager mutex is held for the whole operation. The method rejects repositories without password-change support, derives a new format encryption key from the existing `KopiaRepositoryJSON`, updates in-memory key and password, encrypts repository config with the new key, writes encrypted `kopia.blobcfg`, writes `kopia.repository`, and removes both cached blobs.

## State And Persistence
Mutates in-memory manager password/key and persists both central format blobs. Existing content master key and HMAC secrets remain inside repository config but are re-encrypted under the new password-derived key.

## Dependencies And Integration Points
Depends on `blob.ID` constants and manager fields. Used by repository password rotation workflows; interacts with format cache invalidation and multi-manager cache expiry.

## Risks And Edge Cases
If writing blobcfg succeeds but writing repository blob fails, storage may temporarily contain blobcfg encrypted with the new key while repository config still points to old encrypted format bytes. The method updates in-memory password before all writes complete. Old managers with cached format can continue until their cache expires, as tested.

## Test Signals
`TestChangePassword` covers v3 password-change support, immediate cached readability by old/new managers, old-password failure after cache expiry, and failed new manager creation with the old password.
