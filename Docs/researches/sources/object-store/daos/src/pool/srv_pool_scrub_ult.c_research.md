# sources/object-store/daos/src/pool/srv_pool_scrub_ult.c

## Purpose
`srv_pool_scrub_ult.c` starts, stops, and wires the per-pool-target checksum/tree scrubber ULT. It adapts VOS scrub callbacks to DAOS pool/container state, telemetry, scheduler yielding/sleeping, and automatic target drain on detected corruption or policy decisions.

## Important APIs, types, and functions
The exported functions are `ds_start_scrubbing_ult` and `ds_stop_scrubbing_ult`. The main ULT is `scrubbing_ult`. Callback helpers include `cont_lookup_cb`, `cont_put_cb`, `cont_is_stopping_cb`, `drain_pool_tgt_cb`, `drain_pool_tgt_ult`, and `is_idle`. `sc_add_pool_metrics` creates telemetry counters/gauges/timestamps for completed scrubs, checksum calculations, bytes scrubbed, corruption, duration, busy time, and next-scrub timing under `pool_path/tgt_ID/scrubber/...`.

## Control flow
`ds_start_scrubbing_ult` checks the `DAOS_CSUM_SCRUB_DISABLED` environment variable and, if enabled, creates a deep-stack `SCHED_REQ_SCRUB` ULT. `scrubbing_ult` fills a `struct scrub_ctx` with the VOS pool handle, pool pointer, scheduler callbacks, container lookup/put callbacks, idle test, telemetry pointers, and drain callback. It then repeatedly calls `vos_scrub_pool`; normal iterations sleep for one second, errors sleep for one minute, pool shutdown exits, and `-DER_SHUTDOWN` exits immediately.

When VOS needs a container, `cont_lookup_cb` looks up the pool/container child, copies checksum state and handle into `struct cont_scrub`, and marks the container as scrubbing under its mutex. `cont_put_cb` clears that flag, broadcasts the scrub condition variable, and drops the container reference. If drain is needed, `drain_pool_target` builds an UP/UPIN/NEW rank list and calls `dsc_pool_svc_update_target_state` to transition the local rank/target to DRAIN through the pool service.

## State and persistence behavior
The ULT does not directly persist scrub progress. It drives VOS traversal and checksum verification through `vos_scrub_pool`, updates in-memory container `sc_scrubbing` state to coordinate with container stop, and records process telemetry counters. Drain actions change pool-map target state through the pool service, which is persistent and broadcast to the cluster.

## Dependencies and integration points
This file integrates pool-child startup/shutdown, VOS scrub implementation, container child lookup, server checksum state, Argobots mutex/condition synchronization, telemetry producer APIs, rank discovery, and pool-service target-state update RPCs. It is started by `pool_child_start` only for unrestricted pools and stopped before pool-child reference drain during shutdown.

## Risks and test signals
Risks include stale container scrubbing flags if lookup/put paths are unbalanced, telemetry path format drift that breaks Prometheus label extraction, blocking or racing while draining a target from within scrub context, and repeatedly hammering VOS after persistent scrub errors. Tests should verify scrub ULT disablement, start/stop behavior, metric creation, container stop waiting on `sc_scrubbing`, corruption-to-drain behavior, and clean shutdown while `vos_scrub_pool` is active.
