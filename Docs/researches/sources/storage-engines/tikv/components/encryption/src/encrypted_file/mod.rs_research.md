# sources/storage-engines/tikv/components/encryption/src/encrypted_file/mod.rs

Purpose: This module provides `EncryptedFile`, a helper for atomically reading and writing files whose payload is encrypted by a master-key backend and wrapped with the header format from `header.rs`.

Important APIs and types: It reexports `header::*`, defines `TMP_FILE_SUFFIX`, and exposes `EncryptedFile::new`, `read`, and `write`. The struct stores a base path and file name rather than an open handle.

Control flow: `read` opens the target file, reads all bytes, parses the header, deserializes `EncryptedContent` protobuf from the protected content slice, decrypts through `Backend`, records a histogram, and returns plaintext. `write` creates a random-suffixed temp file, encrypts plaintext, serializes protobuf bytes, writes a V1 header and content, syncs the temp file, atomically renames it over the original, syncs the base directory, and records metrics.

State and persistence behavior: Persistent state is the encrypted file on disk. Writes use temp-file-plus-rename for atomic replacement and directory fsync for durability. Broken temp files are acknowledged by a TODO and not garbage-collected here.

Dependencies and integration points: It uses `crypto::rand::rand_u64`, TiKV `file_system` wrappers, `kvproto::EncryptedContent`, protobuf serialization, `master_key::Backend`, metrics, logging, and `tikv_util::time::Instant`.

Risks: The temp file is opened with create/write but without `create_new`, so an extremely unlikely random-name collision could overwrite an existing temp file. Stale temp cleanup is missing. Reads load the whole file into memory.

Test signals: Unit tests verify missing-file error propagation and plaintext backend write/read roundtrip in a temporary directory.
