# sources/storage-engines/tikv/components/test_pd/src/mocker/service.rs

## Purpose
`Service` is the default in-memory PD mock implementation. It maintains basic cluster membership, store metadata, regions, leaders, bucket reports, feature-gate version, and service GC safe point state for tests that need a functional PD server.

## Important APIs, Types, And Functions
`Service` stores an ID allocator, cached members response, bootstrapped flag, store map with stats, region map, bucket map, leader map, feature-gate string, and service GC safepoint. `header` creates a default cluster response header. `add_store` and `set_cluster_version` allow tests to mutate service state. `make_members_response` builds PD members and leader from bound endpoints.

The `PdMocker` implementation supports `get_members`, bootstrap lifecycle, ID allocation, store get/list/heartbeat, region get/by-id/heartbeat, bucket reports, split/scatter/operator/config placeholders, `put_store`, GC safe point placeholder, and `update_service_gc_safe_point`.

## Control Flow And State
Bootstrap stores the initial store and region and flips `is_bootstrapped`. Heartbeats update region/leader or store stats maps. `alloc_id` uses an atomic counter and has a failpoint to simulate leader connection issues. `update_service_gc_safe_point` keeps a monotonic minimum safe point unless TTL zero resets it.

## Persistence And Integration Points
All state is in-memory. The service is the fallback handler in `PdMock` and backs most RPCs when a case mocker returns `None`. It integrates with `kvproto::pdpb` and `metapb` structures.

## Risks And Test Signals
This is intentionally incomplete compared with real PD: many responses are placeholders, some TODOs note missing cluster-ID and bootstrapped checks, and service safe point handling ignores multiple services. Header errors are returned in OK responses for not-found store/region cases. Tests should avoid relying on exact real-PD scheduling semantics beyond what this mock explicitly tracks.
