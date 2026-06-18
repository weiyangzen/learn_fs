## sources/sync-backup/kopia/internal/blobcrypto/blob_crypto.go

Purpose: whole-blob encryption/decryption utilities that derive blob IDs from hashes and encryption IVs from blob ID suffix bytes.

Important APIs/types/functions: `Crypter`, `Encrypt`, `Decrypt`, and `getIndexBlobIV`.

Control flow, state, and persistence: `Encrypt` hashes payload bytes, constructs `prefix + hex(hash) + optional "-" + suffix`, derives an AES-block-sized IV from the 32 hex characters before the first dash, resets output, and encrypts payload. `Decrypt` derives the same IV from the blob ID and lets the encryptor authenticate/decrypt. The blob ID and encrypted bytes are persisted by callers.

Dependencies and integration points: depends on repository hashing/encryption abstractions, `gather.Bytes`, and `repo/blob.ID`. Used by repository blob storage layers.

Risks and test signals: risks include invalid/short blob IDs, suffix parsing assumptions, and using blob ID-derived IVs that require stable hash naming. Tests cover round trips, ID mismatch failures, invalid IDs, and encryptor failures.
