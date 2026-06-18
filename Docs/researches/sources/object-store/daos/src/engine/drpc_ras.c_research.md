# sources/object-store/daos/src/engine/drpc_ras.c

## Purpose
Builds, logs, and sends DAOS RAS events from the engine to daos_server/control plane over dRPC. It handles generic RAS events, formatted messages, pool service replica update events, SWIM rank-dead events, and self-termination events.

## Important APIs and functions
- `ds_notify_ras_event()` raises a generic event with optional string extended info and default rank.
- `ds_notify_ras_eventf()` formats a message into the fixed RAS field size and delegates.
- `ds_notify_pool_svc_update()` sends a pool-service update event with typed extended info and waits for response.
- `ds_notify_swim_rank_dead()` and `ds_notify_rank_self_terminated()` send predefined state/info events.
- Internal `init_event()`, `log_event()`, `send_event()`, and `raise_ras()` assemble, log, serialize, send, and free event data.

## Control flow
`init_event()` fills mandatory fields: ISO8601-like local timestamp with timezone, event id/type/severity, process id, xstream/thread id, hostname, and message. It then fills optional rank/incarnation/job/pool/container/object/control-operation fields, formatting UUIDs and object IDs as strings. `raise_ras()` logs the event locally, calls `send_event()`, and reports dRPC errors. `send_event()` packs `Shared__ClusterEventReq`, calls `dss_drpc_call(DRPC_MODULE_SRV, DRPC_METHOD_SRV_CLUSTER_EVENT, ...)`, optionally waits/checks response status, and frees allocated event strings.

## State and persistence behavior
No persistent local state. Events are transient protobuf messages sent to control-plane state/logging systems. The local engine log receives a human-readable event string at severity-dependent log level.

## Dependencies and integration
Depends on generated `event.pb-c.h`, server dRPC client, RAS string conversion helpers, engine globals (`dss_hostname`, module info), CRT rank queries, rank-list conversion for pool service info, and server protobuf definitions. Consumers throughout the engine call these notification APIs.

## Risks
There appears to be double-free potential: `send_event()` calls `free_event(evt)` before returning, and `raise_ras()` calls `free_event(evt)` again. If `D_FREE` nulls its argument macro-safe this may be benign, but the pointer fields are not visibly reset in `free_event()`. `init_event()` does not check allocation failures for pool/container/object string fields after `D_ASPRINTF()`. Formatted messages are truncated with a `$` marker but remain null-terminated only because `vsnprintf` wrote the buffer. Fire-and-forget events use `DSS_DRPC_NO_RESP`, so delivery failures may be limited to transport errors.

## Test signals
Tests should cover mandatory-field validation, hostname/module-info failure, default rank fallback, UUID/object formatting, formatted truncation, dRPC transport and response failures, pool service extended info conversion, no-response versus wait-for-response modes, and memory ownership/free behavior in success and failure paths.
