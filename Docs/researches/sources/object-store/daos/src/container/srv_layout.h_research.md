# sources/object-store/daos/src/container/srv_layout.h

## Purpose
Documents and declares the persistent RDB layout for container metadata in the combined pool/container service database. It is the schema contract for root KVS keys, container handle records, container property keys, snapshot metadata, user attributes, and OIT OID mappings.

## Important APIs and types
- Root keys: `ds_cont_prop_cuuids`, `ds_cont_prop_conts`, `ds_cont_prop_cont_handles`.
- `struct container_hdl` is the persistent representation of a container open handle: pool handle UUID, container UUID, handle capabilities/flags/security capabilities.
- Property keys include label, layout, checksum, dedup, redundancy, ACL, owner, snapshot counters/KVS, health status, handles, roots, EC/PDA/perf-domain/global/object versions, scrubber setting, metadata times, handle count, OIT OID map, and EC aggregation epoch.
- `container_flags_t` and `CONTAINER_F_DESTROYING` define persistent service flags.
- `struct co_md_times` stores open and metadata-modify times.
- `cont_prop_default` and `cont_prop_default_v0` are exported default property templates.
- `ds_cont_prop_default_init()` and `ds_cont_prop_default_fini()` manage dynamic defaults.

## Control flow and persistence
This header is declarative but controls how other code traverses RDB: root KVS maps labels to UUIDs, UUIDs to per-container property KVSs, and handle UUIDs to `container_hdl` records. Per-container KVSs hold property values and sub-KVSs for snapshots, user attrs, handle indexes, and snapshot OIT OIDs. RDB layout versioning is tied to the pool global version rather than a standalone container layout version.

## Dependencies and integration
Included by service and target internals, especially `srv_layout.c`, `srv_epoch.c`, and container service creation/query code. The comments explicitly warn that root-key names share a root RDB namespace with pool service layout, so new container root keys must not collide with pool keys.

## Risks
Schema key names are compatibility-sensitive; renaming breaks persisted pools. Some comments mention historical repurposing, such as `ghce` from a zero uint64 to `container_flags_t`, so readers must preserve backward compatibility. The `CONT_PROP_NUM` formula depends on property enum ranges and can silently become wrong if DAOS property enums change unexpectedly.

## Test signals
Schema tests should validate RDB key presence, backward compatibility for older containers, default property initialization, snapshot and OIT sub-KVS creation, and upgrade paths for v0/current property sets.
