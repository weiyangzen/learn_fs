# sources/object-store/rustfs/crates/rio-v2/Cargo.toml

Purpose: this manifest declares `rustfs-rio-v2` as a feature-gated compatibility facade for incremental RustFS migration. Its dependency set shows the crate is not a full replacement for `rustfs-rio`; it reuses the old crate for shared reader traits and replaces specific compression/encryption/index behavior.

Important APIs and dependencies: runtime dependencies include `rustfs-rio` for shared traits/types, `tokio` for async reads, `pin-project-lite` for pinned reader wrappers, `bytes` and `serde_json` for index serialization, `minlz` for S2/minlz compression, `aes-gcm`, `hmac`, `sha2`, `rand`, and `hex` for DARE v2 encryption, multipart key derivation, and tests. `rustfs-utils` supplies compression algorithm type compatibility. Dev dependencies `rustfs-filemeta` and `walkdir` support generated MinIO fixture parsing tests.

State and persistence: the manifest itself has no runtime state, but it fixes the public crate identity, docs URL, categories, and workspace lints. The dependency on `minlz = "1.1.0"` is a direct non-workspace pin and is important for wire compatibility with MinIO-style S2 blocks.

Integration points: `rustfs-rio-v2` exports a subset of new readers while re-exporting `rustfs-rio` traits. Downstream code can switch imports to rio-v2 without losing APIs like `HashReader`, `EtagReader`, `LimitReader`, `TryGetIndex`, and `Index`.

Risks and test signals: because this crate mixes old and new components, semver-compatible changes in `rustfs-rio` can affect rio-v2 behavior. Crypto and compression dependencies are wire-format sensitive; updates require fixture validation. Dev dependencies indicate tests include both unit-level async reader round-trips and ignored MinIO-generated fixture checks.
