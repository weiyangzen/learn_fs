# sources/object-store/daos/src/pool/srv_internal.h

## Purpose

This header is the internal contract for the DAOS pool server implementation. It centralizes process-wide pool configuration, pool module TLS access, metrics layout, IV serialized value types, helper inline functions, and cross-file function declarations for pool service, target, utility, IV, and metrics code.

## Important APIs, types, and functions

- `struct pool_metrics`: telemetry node pointers for operation counters and service gauges.
- `struct pool_tls` and `pool_tls_get()`: xstream-local pool child cache access.
- `ds_pool_skip_for_check()`: check-mode filter for pools that have not been checked.
- IV structures: `pool_iv_map`, `pool_iv_prop`, `pool_iv_conn`, `pool_iv_conns`, `pool_iv_key`, `pool_iv_hdl`, and `pool_iv_entry`.
- Inline IV helpers: `pool_iv_conn_size()`, `pool_iv_conn_next()`, and `pool_iv_conn_ent_size()`.
- Declarations for service lifecycle/RPC handlers, target cache and target RPC handling, pool utilities, IV APIs, and metrics APIs.

## Control flow

The header has no runtime flow beyond inline helpers. It defines how `srv.c` invokes lifecycle functions, how RPC tables refer to handler declarations, how `srv_pool.c` produces IV updates from durable service state, how `srv_target.c` consumes those updates, and how `srv_iv.c` serializes and refreshes the declared IV payloads.

## State and persistence behavior

The IV structures are distributed cache payloads that mirror persistent pool properties, maps, server handles, and connected handle records. `pool_iv_prop` carries the full property set with ACL and service-list data stored in a flexible buffer. `pool_iv_conn` carries handle credentials and layout versions. `pool_tls` is transient per-xstream state.

## Dependencies and integration points

The header depends on GURT lists, DAOS pool-map types, DAOS engine/server declarations, security structures, and telemetry common types. It is included by most pool server implementation files, and its IV structures must remain synchronized with `srv_iv.c`, `srv_pool.c`, and `srv_target.c`.

## Risks and test signals

Property additions must update IV serialization, default properties, persistent layout, and service get/set paths together. `pool_iv_conn_next()` trusts credential sizes and must be paired with bounds validation. `pool_iv_conn_ent_size()` and `pool_iv_conn_size()` are intentionally different. Tests should cover variable-size connection iteration, property serialization after new property additions, check-mode skip behavior, TLS retrieval, and handler signature compatibility.
