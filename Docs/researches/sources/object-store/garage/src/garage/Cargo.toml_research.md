# sources/object-store/garage/src/garage/Cargo.toml

Purpose: manifest for the main `garage` binary crate and its integration test target.

Important APIs/types/functions: binary `garage` at `main.rs`, integration test at `tests/lib.rs`, feature flags for K2V, DB engines, discovery integrations, metrics/telemetry/logging, and bundled/system libraries.

Control flow: build-time dependency and feature wiring. Default features enable bundled libs, metrics, LMDB, SQLite, and K2V.

State and persistence: feature choices control runtime DB engine support, API availability, observability endpoints, logging sinks, and library linkage.

Dependencies and integration points: depends on all major Garage internal crates (`garage_db`, `garage_api_*`, `garage_block`, `garage_model`, `garage_rpc`, etc.) plus CLI/observability/runtime crates. Dev dependencies include AWS SDK and HTTP/testing utilities for integration tests.

Risks: feature combinations must keep internal crate features aligned, especially DB engines and bundled/system libraries. The comment says bundled-libs and system-libs should be mutually exclusive, but Cargo does not enforce it here.

Test signals: integration target plus compile matrix over features. Manifest changes should be validated with at least default-feature build and relevant no-default/system-libs variants.
