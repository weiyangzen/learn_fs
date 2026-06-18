# sources/object-store/daos/src/pool/srv_layout.h

## Purpose

This header documents and declares the DAOS pool server persistent metadata layout. It names every RDB key used for root pool properties, pool-handle storage, pool user attributes, and service operation tracking, and it defines serialized pool-handle value formats.

## Important APIs, types, and functions

- Root property key declarations for map version/buffer, label, ACL, ownership, rebuild/self-heal/reclaim/scrub/checkpoint/reintegration policies, connectable state, handle count, layout/version fields, service-op metadata, server handles, and recovery-container state.
- Nested KVS declarations: `ds_pool_prop_handles`, `ds_pool_attr_user`, and `ds_pool_prop_svc_ops`.
- `struct pool_hdl`: current persisted pool-handle value with flags, security capabilities, machine hostname, credential length, and flexible credentials.
- `struct pool_hdl_v0`: old handle value format.
- `pool_prop_default`, `ds_pool_prop_default_init()`, and `ds_pool_prop_default_fini()`.

## Control flow

The header is declarative. Service code opens root and nested KVS paths, reads/writes the declared keys, and uses `struct pool_hdl` or `pool_hdl_v0` for handle record compatibility. `srv_layout.c` instantiates the symbols and default table.

## State and persistence behavior

This is the durable schema contract. Pool map storage is split into `map_buffer` and `map_version` because `pool_buf` lacks version state. The global layout version covers pool and container metadata. Pool handle keys are UUIDs; values are handle records. User attributes are string-keyed byte arrays. Service-op entries support idempotent RPC result tracking.

## Dependencies and integration points

It depends on DAOS base types and must stay coordinated with container layout because root KVS key suffixes must not collide. It is consumed by pool create/load/query/update/upgrade code, recovery-container reset paths, and IV property propagation.

## Risks and test signals

Adding keys without checking container layout can create metadata collisions. Value type comments are part of the schema contract. The flexible credential field and old handle format require compatibility care. Tests should cover RDB layout creation/upgrades, old handle reads, key collision checks, map version/buffer loading, user attribute round trips, service-op idempotency, and schema declaration/instantiation consistency.
