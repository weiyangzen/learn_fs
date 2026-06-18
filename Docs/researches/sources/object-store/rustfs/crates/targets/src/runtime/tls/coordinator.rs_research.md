## sources/object-store/rustfs/crates/targets/src/runtime/tls/coordinator.rs

Purpose: implements the target-level TLS reload coordinator. It registers TLS-capable targets, builds initial TLS material, spawns per-target polling loops, performs fingerprint-based reload decisions, validates material, applies newly built material, publishes it atomically, and records target TLS metrics.

Important APIs/types/functions: `TargetTlsReloadCoordinator` owns a `RwLock<HashMap<String, TargetReloadEntry>>`. `register` rejects disabled options, calls `target.tls_input_set`, builds initial material, fingerprints configured CA/cert/key files, publishes generation 1 into `TargetTlsRuntimeState`, and starts `spawn_target_poll_loop` for poll/hybrid detection. `unregister` and `shutdown` cancel/abort poll tasks. `force_reload` runs one reload cycle. `build_status_snapshot` serializes runtime status. Private `reload_target_once` performs read/compare/validate/build/apply/publish.

Control flow and state: each poll loop delays its first tick, honors a debounce check against `last_attempt_unix_ms`, then calls `reload_target_once`. Reload updates `last_attempt` first, skips unchanged fingerprints, validates generic TLS files and target-specific files, builds new material before changing state, asks the target to apply it, then stores a new `TargetTlsPublishedState` in `current` and `last_good`. On any failure, current and last-good material stay untouched and `last_error` is set.

Dependencies and integration points: integrates with `ReloadableTargetTls`, `TargetTlsRuntimeState`, target fingerprint/validate modules, metrics, Tokio tasks/channels, and tracing. Targets use the returned runtime state through `TlsReloadAdapter`.

Risks: `min_stable_age` exists in options but this coordinator only uses `debounce`; there is no file mtime stability check. `register` inserts entries by label and would overwrite an existing entry with the same label without first stopping the old poll loop. `bump_generation` is computed from current state before publish, so concurrent forced reloads on the same runtime state could race unless callers serialize them.

Test signals: unit tests cover initial material creation, disabled registration, shutdown/unregister, unchanged reload skip, build/apply/validate failure preservation, clearing errors after success, preserving `last_good`, status snapshots, and generation saturation.
