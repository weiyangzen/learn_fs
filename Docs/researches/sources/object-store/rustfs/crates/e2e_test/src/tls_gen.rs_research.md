# sources/object-store/rustfs/crates/e2e_test/src/tls_gen.rs

Purpose: CLI/library helper for generating a local RustFS TLS and mTLS certificate bundle for e2e tests.

Important APIs and types: `Args` is a `clap::Parser` with `--out-dir`, `--days`, and `--force`. `run` validates positive validity days and delegates to `write_bundle`. `OUTPUT_FILES` defines the seven generated artifacts: server cert/key, CA/public/client CA, and client cert/key. `ensure_writable` prevents overwriting existing bundle files unless `force` is set.

Control flow: `write_bundle` creates the output directory, checks overwrite rules, creates a CA key/certificate, builds a localhost server leaf with DNS and loopback IP SANs, builds a client-auth leaf, and writes all PEM files. `base_params` centralizes subject, validity window, and a five-minute clock-skew allowance.

State and persistence: writes PEM material to the configured directory, defaulting to `target/tls`. It does not persist metadata beyond files and does not clean old bundles.

Dependencies and integration points: uses `rcgen` for CA/leaf certificate generation, `time` for validity, `anyhow` for context-rich errors, and `clap` for CLI parsing.

Risks: generated private keys are unencrypted test assets. `--force` overwrites all bundle files. Validity depends on local system time.

Test signals: unit tests verify full bundle creation, overwrite refusal, and rejection of non-positive `--days`.
