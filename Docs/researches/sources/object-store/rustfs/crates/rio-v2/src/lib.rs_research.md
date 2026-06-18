# sources/object-store/rustfs/crates/rio-v2/src/lib.rs

Purpose: this crate root presents rio-v2 as a compatibility facade. It exports new compression, decompression, encryption, decryption, part-key derivation, and MinIO S2 index helpers while re-exporting the legacy `rustfs-rio` reader traits and wrappers needed by downstream code.

Important APIs: public exports include `CompressReader`, `DecompressReader`, `EncryptReader`, `DecryptReader`, `derive_part_key`, `decode_minio_index_bytes`, and `minio_index_storage_bytes`. Re-exports from `rustfs_rio` include `DynReader`, `Reader`, `ReadStream`, `HashReader`, `EtagReader`, `LimitReader`, `HardLimitReader`, `WarpReader`, `TryGetIndex`, `Index`, `ReaderCapabilities`, checksum helpers, and wrapper constructors.

Control flow and integration: this file has little runtime logic; its main role is API composition. Downstream callers can opt into rio-v2 wire behavior without losing legacy API names. The module tree is private except for selected exports, so implementation details stay encapsulated.

State and persistence: no state is held here. Persistent behavior is delegated to the exported readers and index helpers, and API stability is the main concern.

Risks and test signals: facade crates can accidentally expose inconsistent behavior if legacy and v2 readers make different assumptions about indexes or compression algorithms. The embedded async test verifies `EncryptReader` emits DARE v2 package headers, preserves the configured nonce in the first header, starts subsequent headers at 64 KiB package boundaries, and sets the final flag on the final package.
