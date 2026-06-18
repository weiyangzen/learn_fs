## sources/object-store/rustfs/crates/tls-runtime/src/coordinator.rs

Purpose: implements the shared TLS reload coordinator for foundation TLS material snapshots. It loads TLS material from a `TlsSource`, publishes initial state, detects changed fingerprints, notifies a consumer, updates runtime state, and can spawn a polling loop.

Important APIs/types/functions: `TlsConsumer<M>` requires `on_publish(generation, state)`. `TlsReloadCoordinator` stores `source` and `options`, exposes accessors, `status_snapshot`, `load_initial_snapshot`, `publish_initial_state`, `reload_once`, and `spawn_poll_loop`.

Control flow and state: `publish_initial_state` wraps a snapshot as generation 1 and records generation metrics. `reload_once` marks attempt time, reloads a fresh `TlsMaterialSnapshot`, skips unchanged fingerprints, creates a new `TlsPublishedState` with bumped generation, calls `consumer.on_publish`, then stores to `current` and `last_good`, marks success, clears `last_error`, and records metrics. If consumer publication fails, state is not updated and a publication-fail metric is emitted. `spawn_poll_loop` returns `None` when disabled or non-poll mode, otherwise ticks forever and records last error on failure.

Dependencies and integration points: used by global TLS runtime initialization and consumers that need snapshot updates. Depends on `TlsMaterialSnapshot`, `TlsReloadRuntimeState`, `TlsSource`, metrics, Tokio tasks/time, and tracing.

Risks: poll loop has no shutdown channel; task lifetime is external handle abortion/drop policy. `reload_once` loads material before comparing fingerprints, which is simple but can be expensive for large cert directories. `debounce` and `min_stable_age` options are not applied here.

Test signals: unit test verifies unchanged fingerprint reload returns `Ok(None)`. Crate-level tests verify initial state publication generation.
