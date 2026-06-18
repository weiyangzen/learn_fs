# sources/storage-engines/tikv/components/crypto/src/fips.rs

Purpose: This module centralizes OpenSSL FIPS-mode activation and status logging for TiKV cryptographic code.

Important APIs and state: Public functions are `maybe_enable`, `can_enable`, and `log_status`. `FIPS_VERSION: AtomicUsize` records 0 for disabled, 1 for OpenSSL 1.x FIPS, and 3 for OpenSSL 3 provider mode. `_OPENSSL_VERSION` references `openssl_sys::SSL_version` to keep the dependency visible.

Control flow: `maybe_enable` returns immediately if `can_enable` is false. Under `ossl1`, it calls `openssl::fips::enable(true).unwrap()` and stores 1. Under `ossl3`, it loads the `fips` provider, intentionally leaks it with `mem::forget`, and stores 3. If no expected cfg is active, it logs a warning.

State and persistence behavior: Runtime state is only the atomic status flag and the loaded OpenSSL provider. There is no disk persistence.

Dependencies and integration points: It relies on cfgs emitted by `build.rs`, `openssl`, `openssl-sys`, and `slog-global`. It should be called very early in process startup.

Risks: Provider loading and FIPS enable use `unwrap`, so misconfigured FIPS environments can panic. Calling it late may leave earlier crypto operations outside FIPS mode.

Test signals: Status logs and successful startup under each cfg are the primary signals; no local unit tests are present.
