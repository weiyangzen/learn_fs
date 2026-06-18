# sources/object-store/rustfs/crates/notify/examples/webhook.rs

Purpose: local Axum webhook receiver used by notify demos to inspect delivered event payloads and reset a receive counter.

Important APIs/types/functions: routes `POST /webhook` and `GET /webhook` to `receive_webhook`, `GET /webhook/reset` to query/header-aware reset, and `GET /webhook/reset/{reason}` to path reset. `WEBHOOK_COUNT` is a global `AtomicU64`. `is_service_active` performs a TCP self-check. `convert_seconds_to_date` manually converts Unix seconds for display.

Control flow: parses/binds address `:3020`, starts Axum server, spawns a delayed health check, and shuts down on Ctrl-C. Receive handler prints approximate current time and pretty JSON payload, increments count, and returns 200. Reset handlers print count/reason/headers and reset the atomic.

State and persistence: all state is process-local atomic count and stdout logs. No disk persistence.

Dependencies/integration: uses Axum, Tokio, serde/serde_json, `rustfs_utils::parse_and_resolve_address`, chrono for reset logging, and standard atomics/time.

Risks: `convert_seconds_to_date` ignores leap years and is only approximate; chrono is already available and should be preferred for correctness. `GET /webhook` is registered with a JSON extractor, so ordinary browser GETs without JSON may fail. Server binds a fixed port.

Test signals: no tests. Manual signal is receiving events from `full_demo`/`full_demo_one`; health check only validates TCP accept, not route behavior.
