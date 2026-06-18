# sources/storage-engines/tikv/components/crypto/build.rs

Purpose: The build script configures whether the `crypto` crate compiles with FIPS support and which OpenSSL major-family cfg to enable.

Important APIs and functions: `main` checks the compile-time `ENABLE_FIPS` environment variable. If it is not exactly `1`, it emits `cargo:rustc-cfg=disable_fips`. Otherwise it reads `DEP_OPENSSL_VERSION_NUMBER`, parses it as hex, and emits either `ossl3` for OpenSSL 3.x-or-newer or `ossl1` for older OpenSSL.

Control flow: Non-FIPS builds return early. FIPS builds require the OpenSSL version environment variable from `openssl-sys`; absence causes a panic with a dependency hint.

State and persistence behavior: State is compile-time cfg output consumed by `fips.rs`. No runtime state is stored.

Dependencies and integration points: It depends on Cargo build-script environment propagation from `openssl-sys`.

Risks: `ENABLE_FIPS` is checked with `option_env!`, so it reflects compile-time environment. A malformed version string panics. The threshold treats all pre-3 OpenSSL as `ossl1`, even though API support can vary.

Test signals: Successful cfg emission and build behavior under `ENABLE_FIPS=1` are the useful signals.
