## sources/object-store/garage/src/api/k2v/Cargo.toml

Purpose: Cargo manifest for the `garage_api_k2v` library crate.

Important APIs/types/functions: package metadata, library path `lib.rs`, workspace lints, and dependencies for K2V HTTP API handling.

Control flow: build configuration only.

State/persistence: none.

Dependencies/integration: internal workspace dependencies include `garage_model`, `garage_table`, `garage_util`, and `garage_api_common`. External dependencies include base64, thiserror, tracing, futures, tokio, http, http-body-util, hyper server/http1, serde, serde_json, and OpenTelemetry.

Risks: K2V API relies on common SigV4/server dependencies and hyper feature selection; workspace version changes affect route/auth/body behavior.

Test signals: no manifest-specific tests.
