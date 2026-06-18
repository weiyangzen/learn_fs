# sources/object-store/daos/src/pool/srv_pool_map.h

## Purpose
`srv_pool_map.h` is the narrow internal header for server pool-map target updates. It exposes the state-transition function implemented in `srv_pool_map.c` to the rest of the pool server.

## Important APIs, types, and functions
The only declaration is `ds_pool_map_tgts_update`. It accepts a pool UUID, mutable `struct pool_map`, target ID list, map operation opcode, rank-eviction/domain-update flag, optional output target-map version, and print flag.

## Control flow
There is no executable control flow in this header. It exists to avoid exposing the implementation helpers while allowing pool-service code to update target states through one controlled API.

## State and persistence behavior
The header itself stores no state. The declared function mutates in-memory pool maps and returns enough version information for callers to decide whether downstream rebuild, drain, or reintegration work should run before the pool service persists or broadcasts the map.

## Dependencies and integration points
Consumers need the DAOS pool-map type definitions and target-list structures before including this header. The main integration point is pool-service map update handling in `src/pool/srv_pool.c`.

## Risks and test signals
The risk is interface drift: operation semantics, `evict_rank`, or `tgt_map_ver` behavior must remain synchronized with the implementation and callers. Build coverage catches signature drift; behavioral coverage belongs to tests around `ds_pool_map_tgts_update`.
