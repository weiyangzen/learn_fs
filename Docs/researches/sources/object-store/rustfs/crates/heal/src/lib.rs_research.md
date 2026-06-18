# sources/object-store/rustfs/crates/heal/src/lib.rs

The heal crate root exports the main public API and owns process-wide heal runtime singletons. It re-exports `Error`, `Result`, `HealManager`, task request/option/priority/type types, and `HealChannelProcessor`. It also manages a global AHM/heal services `CancellationToken`, the global `HealManager`, the global mutex-protected channel processor, and relaxed atomic gauges for active task and queue counts.

`init_heal_manager` constructs and starts `HealManager`, stores it in a `OnceLock`, initializes `rustfs_common::heal_channel`, creates/stores a `HealChannelProcessor`, and spawns a Tokio task that drives the processor. Initialization errors are returned for duplicate singleton setup; background processor failures are logged. `shutdown_ahm_services` cancels the global token if one exists.

All state here is process-local; persistence is handled by downstream storage/task code. Integration points are the common heal channel, Tokio runtime, `HealStorageAPI`, tracing, atomics, `OnceLock`, and cancellation tokens. Risks are one-shot initialization without reset, `create_ahm_services_cancel_token` panicking on duplicate initialization, and background processor failures requiring log/metric monitoring.
