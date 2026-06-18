# sources/storage-engines/tikv/components/tracker/src/future.rs

Purpose: generic future polling instrumentation wrapper.

Important APIs/types/functions: `FutureTrack`, `track`, and internal pinned `Tracker<F, T>`.

Control flow: wrapper calls `on_poll_begin`, polls the inner future, then calls `on_poll_finish` before returning the poll result.

State and persistence: wrapper owns the future and tracker object; no persistence.

Dependencies/integration: uses `pin-project` for safe projection and is suitable for recording per-poll timing or resource state around async execution.

Risks: `on_poll_finish` is skipped if the inner poll panics; tracker hooks must be cheap because they run on every poll.

Test signals: no local tests; used as a primitive by higher-level tracking.
