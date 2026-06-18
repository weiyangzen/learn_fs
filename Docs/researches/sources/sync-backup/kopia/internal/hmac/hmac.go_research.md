# sources/sync-backup/kopia/internal/hmac/hmac.go

Purpose: appends and verifies HMAC-SHA256 checksums for gathered byte sequences, mainly to protect cached data from corruption or tampering.

Important APIs/types/functions: `Append`, `VerifyAndStrip`, `gather.Bytes`, `gather.WriteBuffer`, `crypto/hmac`, `sha256`, and `io.CopyN`.

Control flow: `Append` writes the original input to output, writes the same input to an HMAC hasher, and appends the 32-byte signature. `VerifyAndStrip` rejects inputs shorter than the signature, streams all but the signature into both the hasher and output, reads the trailing signature, and compares with `hmac.Equal`.

State/persistence behavior: no internal state is kept. The output format is data followed by raw SHA-256 HMAC bytes; callers persist it where needed, such as list cache blobs.

Dependencies/integration: integrates with gather buffers and `listcache`. Uses constant-time comparison through `hmac.Equal`.

Risks/test signals: `Append` ignores write errors because `gather.WriteBuffer` writes are expected not to fail; a different output implementation is not supported. `VerifyAndStrip` writes plaintext into output before signature validation completes, so callers must discard output on error.
