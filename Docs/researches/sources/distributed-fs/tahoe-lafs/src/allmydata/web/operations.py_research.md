# sources/distributed-fs/tahoe-lafs/src/allmydata/web/operations.py

## Purpose
Maintains in-memory operation handles for long-running WebAPI jobs such as deep checks, manifests, and deep stats. It exposes `/operations/<ophandle>` resources, supports cancellation, retention timers, release-after-complete, and reload/cancel template helpers.

## Important APIs, Types, And Functions
`OphandleTable` is both a Twisted `Resource` and `service.Service`. It stores `(monitor, renderer, when_added)` tuples in `handles` and delayed calls in `timers`. Key methods are `add_monitor`, `_operation_complete`, `redirect_to`, `getChild`, `_set_timer`, `_release_ophandle`, and `stopService`. `ReloadMixin` provides `refresh` and `reload` renderers for monitor-backed result elements.

## Control Flow
Directory operations require an `ophandle` argument before calling `add_monitor`. The table records the monitor/renderer, optionally schedules `retain-for`, and attaches `_operation_complete` to `monitor.when_done()`. `redirect_to` constructs `/operations/<handle>` and preserves `output`. Later `getChild` validates the handle, processes `POST t=cancel`, optionally refreshes timers, releases handles after complete if requested, converts monitor `Failure` status to a failed Deferred, and otherwise returns the renderer. Completed handles without explicit retention are retained first as uncollected and then as collected after a GET.

## State And Persistence
All state is process-local and lost on node restart. Default retention constants are four days for uncollected handles and one day after collection. Timers use an injected clock for tests or the global Twisted reactor. Cancellation delegates to the monitor. No filesystem or database persistence is used.

## Dependencies And Integration Points
It depends on Twisted resources, services, Deferreds, reactor timers, URLPath, Hyperlink URLs, and shared `get_arg`/`WebError`/`boolean_of_arg` helpers. `directory.py` registers monitor-backed renderers here; `check_results.py` and `directory.py` elements use `ReloadMixin` to present reload/cancel affordances.

## Risks And Test Signals
Risks include unbounded handle growth if timers are not set or cancelled correctly, byte/string mismatches for handle keys, invalid `retain-for` values raising raw conversion errors, race behavior when a handle is cancelled/released while being fetched, and process-local loss of operation status. Tests should use deterministic clocks for timer expiry, cover cancellation, release-after-complete, unknown handles, `Failure` monitor status, redirect URL construction, and directory operations that require `ophandle`.
