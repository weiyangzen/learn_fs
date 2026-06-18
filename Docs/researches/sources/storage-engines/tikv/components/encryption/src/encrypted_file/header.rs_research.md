# sources/storage-engines/tikv/components/encryption/src/encrypted_file/header.rs

Purpose: This module defines the binary header format for encrypted files and validates header/content integrity through version, length, and CRC32 checks.

Important APIs and types: `Version::{V1,V2}` distinguishes files containing only encrypted content from files with unencrypted trailing log records. `Header` stores `version`, `crc32`, and `size`. Public methods are `Header::new`, `Header::parse`, `Header::to_bytes`, and `Header::version`.

Control flow: `Header::new` computes CRC32 over serialized encrypted content and records its length. `parse` requires a 16-byte header, decodes version, CRC32, and big-endian size, then enforces exact remaining size for V1 or at-least size for V2. It slices content and remaining bytes, recomputes CRC32, and returns an error on mismatch.

State and persistence behavior: The header is persisted at the beginning of encrypted files as 1 version byte, 3 reserved bytes, 4 CRC bytes, and 8 content-size bytes. V2 permits additional trailing data after the encrypted content.

Dependencies and integration points: It is used by `encrypted_file/mod.rs` before protobuf parsing/decryption. It depends on `byteorder`, `crc32fast`, `Write`, and TiKV boxed errors.

Risks: CRC32 is corruption detection, not authentication; cryptographic integrity must come from the encrypted content/backend. Large encoded sizes are cast to `usize` after length checks and should be reviewed for 32-bit targets.

Test signals: Tests cover empty header roundtrip, successful parse with content, missing content error, and CRC mismatch error.
