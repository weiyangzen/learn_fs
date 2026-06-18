# sources/object-store/rustfs/crates/io-core/Cargo.toml

Purpose: crate manifest for `rustfs-io-core`, described as zero-copy reader and writer implementations for RustFS.

Important configuration: package metadata inherits version, edition, license, repository, rust-version, and homepage from the workspace. The crate disables doctests for the library. Keywords and categories position the crate around zero-copy readers/writers and filesystem tooling.

Dependencies: runtime dependencies are `bytes`, `thiserror`, `tokio` with `io-util`, `fs`, `rt`, and `sync`, `memmap2`, and `rustfs-io-metrics`. A Linux-specific target dependency enables Tokio's `io-uring` feature. Dev dependencies enable Tokio `rt-multi-thread` and `macros` for async tests.

Integration points: this manifest makes `io-core` a low-level crate with limited dependencies, suitable for reuse by storage and object paths without pulling in higher-level RustFS crates. Metrics integration is explicit through `rustfs-io-metrics`.

Risks: Linux `io-uring` is enabled as a target-specific Tokio feature, but the listed researched `direct_io.rs` implementation uses synchronous `FileExt::read_at`, not io-uring. The crate description emphasizes zero-copy, while some implementation paths copy mmap/file data into `Bytes`, so downstream users should rely on concrete APIs rather than the manifest description alone.

Test signals: Tokio async testing support is enabled, and the researched modules contain many unit tests. Doctests are disabled, so example snippets in docs are not compiled by `cargo test --doc`.
