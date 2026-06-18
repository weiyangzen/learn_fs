## sources/security-integrity/encfs/Cargo.toml

Purpose: Rust workspace/package manifest for EncFS 2.0 beta. It defines binaries, dependencies, build script dependencies, dev dependencies, and i18n metadata.

Important APIs and types: workspace includes `"."` and excludes `fuzz`; package uses edition 2024; build dependencies `prost-build` and `protoc-bin-vendored`; runtime dependencies cover crypto (`aes`, `aes-gcm`, `aes-gcm-siv`, `argon2`, `pbkdf2`, `sha*`, `hmac`, `zeroize`), FUSE (`fuse_mt`, `libc`), config serialization (`quick-xml`, `prost`, `serde`, `base64`), CLI/i18n/logging (`clap`, `rust-i18n`, `env_logger`, `log`), and utility crates.

Control flow: declarative; build.rs compiles protobufs. State and persistence are Cargo lock/build artifacts. Integration defines `encfsctl` and `encfsr` binaries. Risks include edition/toolchain requirements, native FUSE/OpenSSL-related dependencies, and crypto dependency compatibility. Test signal comes from dev dependency `tar` plus CI/Taskfile commands rather than manifest scripts.
