# sources/storage-engines/wiredtiger/src/include/load_control.h

## Purpose
Defines connection-level load-control state used to reject or throttle reads/writes when cache pressure reaches configured thresholds.

## Important APIs, Types, And Functions
- `struct __wt_connection_load_control` stores `control_threshold`, atomic/shared `read_load` and `write_load`, maximum byte-equivalent load bounds, and a `flags` field.
- `WT_CONN_LOAD_CONTROL` enables the load-control checks.

## Control Flow
This header only declares state. Runtime checks are implemented in `load_control_inline.h`, where readers compare current load counters against `control_threshold` if the enable flag is set.

## State And Persistence Behavior
Load-control fields are connection memory state, not persistent metadata. `read_load`, `write_load`, and max values are marked `wt_shared`, indicating concurrent access from multiple threads and requiring atomic or carefully synchronized reads/writes.

## Dependencies And Integration Points
The struct is embedded in `WT_CONNECTION_IMPL` and accessed via `S2C(session)->load_control`. It depends on WiredTiger's flag macros and atomic/shared-field conventions.

## Risks
Threshold tuning affects user-visible availability and latency. Non-atomic reads of shared fields would be unsafe; callers should use the inline helpers or atomic accessors. A disabled flag must reliably bypass rejection even if stale load counters are high.

## Test Signals
Load-control tests should exercise disabled/enabled states, read and write thresholds, boundary equality at `control_threshold`, concurrent updates to load counters, and integration with cache eviction/load measurements.
