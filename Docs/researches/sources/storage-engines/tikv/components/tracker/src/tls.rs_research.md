# sources/storage-engines/tikv/components/tracker/src/tls.rs

Purpose: thread-local active tracker token management and future wrapper that propagates that token while polling.

Important APIs/types/functions: `set_tls_tracker_token`, `clear_tls_tracker_token`, `get_tls_tracker_token`, `with_tls_tracker`, and `TlsTrackedFuture`.

Control flow: callers set a token in TLS; `with_tls_tracker` resolves it through `GLOBAL_TRACKERS`. `TlsTrackedFuture::new` captures the current TLS token, and each poll temporarily installs it, polls the inner future, then clears TLS.

State and persistence: per-thread `Cell<TrackerToken>` only.

Dependencies/integration: used by `tikv_util::yatp_pool::FuturePool` to preserve request tracker context across executor threads.

Risks: TLS is cleared after every poll, so nested code must rely on the wrapper; panics during poll skip the clear path. Invalid tokens are treated as no tracker.

Test signals: no local tests; behavior is indirectly exercised by future pool tracking.
