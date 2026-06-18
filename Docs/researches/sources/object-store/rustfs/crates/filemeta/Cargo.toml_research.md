# sources/object-store/rustfs/crates/filemeta/Cargo.toml

Purpose: crate manifest for `rustfs-filemeta`, the metadata encoding/decoding and object-version model used by RustFS object storage.

Important declarations: library doctests are disabled. Dependencies include MessagePack (`rmp`, `rmp-serde`), `serde`, `bytes`, `time`, `uuid`, `tokio` IO, `xxhash-rust`, `crc-fast`, `byteorder`, `rustfs-utils` with hash/http features, `s3s`, `regex`, `arc-swap`, `tracing`, and `thiserror`. Criterion and tempfile are dev-only. The `xl_meta_bench` benchmark is registered with `harness = false`.

State and persistence: the manifest defines the persistence-format stack: MessagePack encoding, xxhash CRCs, UUID/time handling, byte buffers, S3 headers, and async reading. It also exposes the crate for docs.rs.

Dependencies and integration: this crate sits below ecstore and object APIs, sharing metadata types via `pub use` in `src/lib.rs`. `rustfs-utils` and `s3s` link metadata with HTTP/S3 headers and restore/tiering semantics.

Risks: broad dependency surface means workspace feature changes can affect serialization or HTTP metadata behavior. Disabling doctests leaves examples uncompiled. Benchmark availability depends on dev dependency alignment with workspace Criterion.

Test signals: manifest declares Criterion bench coverage for XL metadata creation, parsing, serialization, round-trip, stats, and integrity.
