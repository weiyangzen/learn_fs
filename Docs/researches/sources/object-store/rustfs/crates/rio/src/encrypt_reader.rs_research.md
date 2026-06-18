<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/encrypt_reader.rs -->
# sources/object-store/rustfs/crates/rio/src/encrypt_reader.rs

## Purpose
Implements streaming AES-256-GCM encryption and decryption wrappers for `tokio::io::AsyncRead`. `EncryptReader` converts plaintext into framed encrypted blocks; `DecryptReader` reverses that framing, supports multipart object segments, validates plaintext length and CRC32, and keeps compatibility with older nonce layouts.

## Important APIs, types, and functions
- `EncryptReader<R>::new` and `new_multipart` wrap an async reader with a 32-byte key and 12-byte nonce.
- `DecryptReader<R>::new` and `new_multipart` consume encrypted block streams and optionally advance through explicit multipart part numbers.
- `poll_read` on both readers is the main state machine.
- `multipart_part_nonce`, `derive_part_nonce`, `derive_legacy_part_nonce`, `derive_block_nonce`, and `derive_nonce_offset` define nonce derivation.
- `TryGetIndex`, `EtagResolvable`, and `HashReaderDetector` capabilities are delegated to the inner reader.

## Control flow
`EncryptReader::poll_read` first drains any buffered framed bytes, then reads up to `ENCRYPTION_BLOCK_SIZE` bytes from the inner reader. Non-empty reads are CRC32-hashed, encrypted with a nonce derived from the base nonce plus `block_index`, prefixed with an 8-byte header and plaintext-length uvarint, buffered, and copied to the caller. EOF emits a `0xFF` terminator header once. `DecryptReader::poll_read` drains plaintext first, then incrementally reads an 8-byte header, handles `0xFF` segment terminators, reads the declared payload, decodes the plaintext length, tries primary and legacy nonces, checks plaintext length and CRC32, buffers plaintext, and advances the block counter.

## State and persistence behavior
All state is in-memory stream state: buffered bytes, current offsets, block index, multipart part index, header progress, payload progress, and completion flags. The wire format is persisted wherever encrypted object data is stored: 8-byte headers, uvarint plaintext lengths, ciphertext plus GCM tag, CRC32, and terminator records. Multipart streams persist each part as its own terminated encrypted segment.

## Dependencies and integration points
Depends on `aes_gcm`, `crc_fast`, `rustfs_utils` uvarint helpers, `pin_project_lite`, Tokio `AsyncRead`, and `tracing`. It integrates with `HashReader`, `EtagReader`, compression readers, and compression indexes via capability delegation. Multipart nonce behavior is important for object upload/download paths that concatenate encrypted part streams.

## Risks and edge cases
The file comment calls the crypto wrapper demonstrational, but it is used as object data plumbing, so nonce uniqueness is critical. The current decryptor indexes `ciphertext_buf[0..16]` before checking the payload is at least 16 bytes, which can panic on malformed short payloads. The 24-bit header length limits payload sizes and must stay compatible with block sizing. Legacy nonce fallbacks intentionally accept weaker historical streams but widen the accepted ciphertext surface.

## Test signals
Tests cover round-trip encryption, large 1 MiB payloads, tiny chunked reads, pending reads, `ReaderStream` and `HardLimitReader` integration, multipart segment concatenation, distinct per-block nonces, non-collision across parts, and legacy single-nonce and multipart nonce layouts.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/encrypt_reader.rs -->
