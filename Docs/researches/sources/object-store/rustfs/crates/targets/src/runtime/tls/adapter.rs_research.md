## sources/object-store/rustfs/crates/targets/src/runtime/tls/adapter.rs

Purpose: provides `TlsReloadAdapter<M>`, the small per-target handle that connects a concrete `ReloadableTargetTls` implementation to `TargetTlsReloadCoordinator`. Targets can hold `Option<TlsReloadAdapter<M>>` and use it on their send hot path while retaining a legacy fallback when registration fails.

Important APIs/types/functions: `try_register(target, options, coordinator)` delegates to `coordinator.register`, logs success or failure, and returns `Some(adapter)` only after initial material has been built and, for poll/hybrid mode, the background loop has been spawned. `current_material()` clones the current `Arc<M>` from the coordinator-managed `ArcSwap`; `generation()` returns the active generation; `status_snapshot()` calls `TargetTlsReloadCoordinator::build_status_snapshot`; `runtime_state()` exposes the shared state for cleanup; `unregister()` stops the coordinator entry for the target label.

Control flow and state: the adapter stores `Arc<TargetTlsRuntimeState<M>>` plus the `TlsReloadOptions` used for snapshots. Cloning the adapter shares the same runtime state and options. It never mutates TLS material directly; all mutation is owned by the coordinator.

Dependencies and integration points: depends on target TLS config/coordinator/state/trait modules, `Arc`, and tracing. It is the ergonomic boundary used by AMQP, SQL, webhook, or other TLS-capable target implementations.

Risks: failed registration silently degrades to fallback behavior by returning `None`; callers must preserve and exercise the fallback. `unregister` is best-effort and logs warnings instead of propagating errors.

Test signals: tests use a fake target to prove success builds material once, failure returns `None`, clones share state, and snapshots expose the target label and reload enablement.
