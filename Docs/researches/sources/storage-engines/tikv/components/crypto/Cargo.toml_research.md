# sources/storage-engines/tikv/components/crypto/Cargo.toml

Purpose: This manifest defines TiKV's small `crypto` shim crate, used for cryptographic utilities with FIPS-aware OpenSSL setup.

Important APIs and settings: Package metadata sets name `crypto`, version `0.0.1`, edition 2021, Apache-2.0 license, and `publish = false`. Dependencies are `openssl`, `openssl-sys`, `slog`, and `slog-global` from the workspace. The lint configuration whitelists custom cfgs `ossl1`, `ossl3`, and `disable_fips`.

Control flow: Cargo uses this file to compile `build.rs`, expose OpenSSL version information, and allow code guarded by the custom cfgs.

State and persistence behavior: It is build metadata only. No runtime state is defined here.

Dependencies and integration points: `openssl-sys` is intentionally kept as a direct dependency so the build script can read `DEP_OPENSSL_VERSION_NUMBER`. The encryption component depends on this crate for random-number generation.

Risks: Removing `openssl-sys` or the custom-cfg lint allowance breaks FIPS build detection or produces unexpected-cfg warnings.

Test signals: Build success under FIPS and non-FIPS configurations is the main signal.
