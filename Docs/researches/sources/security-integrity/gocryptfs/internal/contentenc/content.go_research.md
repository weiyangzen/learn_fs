# sources/security-integrity/gocryptfs/internal/contentenc/content.go

Purpose: This file implements block-level encryption and decryption for gocryptfs file contents.

Important APIs and types: `ContentEnc` owns a `cryptocore.CryptoCore`, block sizes, zero-block sentinels, and buffer pools. Key functions include `New`, `PlainBS`, `CipherBS`, `DecryptBlocks`, `DecryptBlock`, `EncryptBlocks`, `EncryptBlock`, `EncryptBlockNonce`, `MergeBlocks`, `Wipe`, `concatAD`, and internal parallel encryption helpers.

Control flow and state: Encryption prepends a random or caller-supplied nonce and authenticates block number plus file ID as associated data. Decryption handles empty blocks, all-zero sparse holes, nonce extraction, all-zero nonce rejection, AEAD open, and pooled buffers. Large writes may be split across goroutines.

Dependencies and integration points: Used by file I/O, config key wrapping, symlink/xattr crypto, fsck, and tests. Depends on FUSE max write size and crypto backends.

Risks and test signals: Security risks include nonce misuse, wrong associated data, buffer reuse bugs, and sparse-hole handling. Signals include encrypt/decrypt round trips, tamper failures, block split/merge tests, and AESSIV nonce restrictions.
