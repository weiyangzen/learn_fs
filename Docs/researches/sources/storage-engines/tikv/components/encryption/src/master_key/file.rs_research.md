# sources/storage-engines/tikv/components/encryption/src/master_key/file.rs

Purpose: Implements a secure master-key backend backed by a local key file. It reads a hex-encoded AES-256-GCM key and delegates encryption/decryption to the in-memory GCM backend.

Important APIs and types: `FileBackend::new` validates and loads the key file. `Backend` implementation provides sync `encrypt`, `decrypt`, and `is_secure`. `AsyncBackend` implementation forwards to the sync methods.

Control flow: `new` opens the file, checks its exact size as 64 hex bytes plus newline, reads it completely, verifies newline termination, decodes hex, then constructs `MemAesGcmBackend`. `encrypt` generates a fresh GCM IV and encrypts content; `decrypt` validates and authenticates through the memory backend.

State and persistence behavior: The backend keeps the decoded master key in memory. It does not persist new state; encrypted metadata stores IV, method, ciphertext, and GCM tag in `EncryptedContent`.

Dependencies and integration: Used by data-key dictionary encryption and by multi-master-key restore. It depends on `file_system::File`, crate `AesGcmCrypter`/`Iv`, and master-key metadata handled in `mem.rs`.

Risks: Strict file sizing prevents accidental large reads but rejects files without trailing newline or with extra whitespace. The decoded key remains in process memory for backend lifetime. Authentication failures surface as `WrongMasterKey`, which triggers previous-key fallback in the manager.

Test signals: Tests verify known AES-256-GCM vectors, successful encrypt/decrypt round trips, GCM tag mismatch as `WrongMasterKey`, and missing tag as metadata corruption.
