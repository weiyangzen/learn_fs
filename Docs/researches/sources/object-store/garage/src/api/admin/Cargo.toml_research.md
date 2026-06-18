# sources/object-store/garage/src/api/admin/Cargo.toml

Purpose: declares the `garage_api_admin` Rust crate, which builds the Garage Admin API server library from `lib.rs`.

Important configuration: package metadata identifies version `2.3.0`, edition 2018, AGPL-3.0 license, repository, and README. The `[lib]` section points at `lib.rs`. Dependencies include Garage workspace crates (`garage_model`, `garage_block`, `garage_table`, `garage_util`, `garage_rpc`, `garage_api_common`) and external API/runtime crates such as `hyper`, `http`, `tokio`, `serde`, `utoipa`, `argon2`, `chrono`, `thiserror`, `paste`, `format_table`, `opentelemetry`, and optional Prometheus support.

Control flow and state: no runtime control flow. Feature flags gate optional integrations: `metrics` enables Prometheus exporter dependencies, and `k2v` forwards to `garage_model/k2v`. Lints are inherited from the workspace.

Dependencies/integration: this manifest is the integration surface between the admin API implementation and the workspace dependency graph. It also controls whether metrics endpoints can expose Prometheus data and whether K2V tables appear in node statistics.

Risks: `hyper` is built without default features and with `server`/`http1`, so HTTP behavior depends on common server abstractions for missing capabilities. Optional metrics code must stay cfg-gated with the feature. Workspace version drift can break schema, RPC, or helper assumptions across Garage crates.

Test signals: run crate checks with default features, with `--features metrics`, and with `--features k2v`. API schema generation and admin server tests should confirm optional fields compile under all feature combinations.
