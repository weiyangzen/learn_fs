# sources/object-store/rustfs/crates/obs/src/metrics/mod.rs

Purpose: top-level metrics module facade for RustFS observability. It declares metrics submodules and re-exports the collector, config, reporting, and runtime scheduler APIs.

Important APIs/types: modules `collectors`, `config`, `report`, `scheduler`, `schema`, and `stats_collector`. Re-exports include `PrometheusMetric`, `report_metrics`, collector/config items, and scheduler runtime controller/status types and init functions.

Control flow: compile-time module organization only.

State/persistence: no state.

Dependencies/integration: downstream code can import metrics APIs from `crate::metrics::*` instead of individual submodules. Scheduler runtime types exported here are likely used by service status/admin endpoints.

Risks: broad `pub use collectors::*` and `pub use config::*` make many internals part of the crate API. Removing or renaming exports can break downstream modules even if implementation still exists. `stats_collector` is declared but not publicly glob-re-exported here.

Test signals: no local tests; compile-time usage across the crate validates the facade.
