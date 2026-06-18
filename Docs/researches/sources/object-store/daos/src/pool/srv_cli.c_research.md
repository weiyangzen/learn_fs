# sources/object-store/daos/src/pool/srv_cli.c

## Purpose

This file provides server-side wrappers for calling DAOS client pool APIs and pool service RPCs from within the engine. It lets management, rebuild, scrub, and other server subsystems perform pool operations without holding a normal client pool handle. The core pattern is a generic replicated-service call loop (`dsc_pool_svc_call`) plus operation-specific init/consume/fini callbacks.

## Important APIs, types, and functions

- `dsc_pool_open()` / `dsc_pool_close()`: create and release server-side `dc_pool` objects.
- `dsc_pool_tgt_exclude()` / `dsc_pool_tgt_reint()`: task wrappers around client target-update APIs.
- `struct dsc_pool_svc_call_cbs`: callback table for pool-service RPC wrappers.
- `dsc_pool_svc_call()`: common RSVC leader-selection, retry, timeout, send, callback, and backoff loop.
- Query APIs: `dsc_pool_svc_query()`, `dsc_pool_svc_query_target()`, `process_query_result()`, and `pool_map_get_dead_ranks()`.
- Administrative APIs: check/evict, get/set properties, extend, update target state, update/delete ACL, upgrade, rebuild stop/start, and evaluate self-heal.

## Control flow

`dsc_pool_svc_call()` initializes an `rsvc_client`, starts a backoff sequence, chooses a pool-service replica, creates a request with `ds_pool_req_create()`, invokes the init callback, caps the CRT timeout to the absolute deadline, sends with `dss_rpc_send()`, and passes completion plus leader hints to `rsvc_client_complete_rpc()`. Non-retryable pool replies are handed to the consume callback, which can finish, retry with backoff, or retry immediately. Query uses a bulk map buffer and retries immediately on `-DER_TRUNC` with the service-returned required map size.

## State and persistence behavior

The file does not directly write RDB state. Its RPCs ask the pool service to mutate durable target states, properties, ACLs, upgrade state, rebuild state, and handle records. Locally it manages transient `dc_pool` references, task objects, rank lists, bulk handles, and sanitized ACL principal strings.

## Dependencies and integration points

It depends on the DAOS client pool stack, management system attach, RSVC client APIs, pool RPC helpers from `rpc.h`, CART RPC send/timeout APIs, pool-map conversion helpers, SWIM state through CART group rank state, and `dss_get_module_info()`. Server subsystems call these wrappers for control-plane pool operations.

## Risks and test signals

Deadline handling is strict and can force `-DER_TIMEDOUT` when less than one second remains. Query callers must provide rank-list output pointers matching requested `pi_bits`. Immutable property checks in `dsc_pool_svc_set_prop()` protect create-time/internal fields. Tests should cover not-leader hints, retryable errors, `-DER_TRUNC` map retry, timeout capping, invalid target state, property rejection, SWIM dead-rank reporting, ACL string sanitation, and bulk cleanup on retries.
