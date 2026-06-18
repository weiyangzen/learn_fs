# sources/storage-engines/tikv/components/tracker/src/metrics.rs

Purpose: Prometheus metric for tracker slab capacity failures.

Important APIs/types/functions: `SLAB_FULL_COUNTER`.

Control flow: lazy-static registration creates a counter incremented when a tracker slab shard refuses insertion due to maximum capacity.

State and persistence: process-local Prometheus counter only.

Dependencies/integration: used by `slab.rs` insert failure path.

Risks: failure means the request loses tracker detail while continuing with `INVALID_TRACKER_TOKEN`; alerting depends on this counter being scraped.

Test signals: no direct metric test.
