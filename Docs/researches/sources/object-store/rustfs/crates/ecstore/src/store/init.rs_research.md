# sources/object-store/rustfs/crates/ecstore/src/store/init.rs

## Purpose
This file owns `ECStore` construction and post-construction initialization. It converts endpoint pool topology into initialized disk handles, validates/loads erasure format metadata, builds `Sets` pools, publishes global local-disk and deployment identity state, loads pool/rebalance metadata, and starts background store services such as lifecycle expiry, stale multipart cleanup, transition state, tiering migration, and optional decommission resume.

## Important APIs, Types, And Functions
- `ECStore::new(address, endpoint_pools, ctx) -> Result<Arc<Self>>` is the high-level constructor. It initializes peer identity, disks, storage formats, `Sets`, global local disk maps, `S3PeerSys`, `PoolMeta`, decommission cancelers, and global object layer publication.
- `ECStore::init(&Arc<Self>, rx) -> Result<()>` performs second-stage initialization after the `ECStore` is built: rebalance metadata load/start, pool metadata load/validation/save, resumable decommission scheduling, bucket monitor setup, lifecycle/tiering background routines, and tier manager initialization.
- `pool_first_endpoint_is_local` and `should_resume_local_decommission` protect startup ownership decisions so expansion/decommission work is resumed only by the node owning the first endpoint in the relevant pool.
- `resume_local_decommission_after_init` waits and retries decommission resume, handling `ConfigNotFound` with a bounded retry loop and restarting workers if the decommission state is already running.
- `resolve_store_init_stage_result` wraps stage-specific failures with startup context.
- `single_pool` is a small predicate used throughout store handlers.

## Control Flow
`ECStore::new` first derives host/port from the socket address or global config and calls `init_local_peer`. For each endpoint pool it computes/validates parity, initializes disks with cleanup and health checks enabled but not started, checks fatal disk errors, then retries `connect_load_init_formats` up to ten times with exponential backoff. On each format retry it listens for Ctrl-C and resets disk health so reused disk handles can reconnect to peers that came online later. After formats load, health checks are enabled, deployment IDs are verified across pools, local disks are collected, and `Sets::new` builds each pool.

Once pools are assembled, non-distributed deployments publish local disk path mappings. The constructor builds `ECStore`, conditionally publishes the global deployment ID, retries `ec.init(ctx)` up to a local budget, publishes the object layer, attaches any global bucket monitor, and returns the shared store.

`ECStore::init` is stage-oriented. It records boot time, loads rebalance metadata, starts rebalance if metadata exists, loads pool metadata from the first pool, validates it against current pools, and either installs the loaded metadata or creates/saves a repaired `PoolMeta`. Only the first local cluster node persists validated pool metadata to avoid distributed startup races. It then resolves resumable decommission pool command lines against current endpoints, schedules a delayed local resume task if the first resumable pool is local, initializes bucket/lifecycle/tiering background systems, and logs rather than fails tier manager init errors.

## State And Persistence Behavior
The file persists or updates several pieces of cluster state:
- Erasure format metadata is loaded from disks and deployment IDs are validated across pools. Nil deployment IDs are replaced with a new UUID.
- Global deployment ID is set once if missing.
- `GLOBAL_LOCAL_DISK_MAP` is populated in non-distributed mode from local disk endpoint strings.
- `PoolMeta` is loaded from storage, validated, and sometimes saved back through `PoolMeta::save` when topology metadata requires repair.
- `rebalance_meta` is loaded into an `RwLock<Option<_>>` and can trigger rebalance startup.
- Decommission state is not directly persisted here, but resumable decommission pools from `PoolMeta` can cause delayed calls into `decommission` and `spawn_decommission_routines`.
- Background lifecycle, stale multipart cleanup, transition, tier migration, and tier manager initialization establish long-running runtime state.

## Dependencies And Integration Points
The module depends on endpoint topology, disk initialization, erasure format loading, storage class parity validation, pool metadata, global object layer state, bucket monitor globals, tiering config, lifecycle modules, `S3PeerSys`, `Sets`, tracing, Tokio timing/signal handling, and cancellation tokens. It is the bridge between raw endpoint configuration and all higher-level `ECStore` object/list/multipart/rebalance handlers.

## Risks And Edge Cases
- Startup behavior is heavily global-state-dependent; ordering mistakes can affect local disk maps, deployment ID publication, bucket monitor, and object layer visibility.
- Format loading retries reuse disk handles and must reset transient health markers; without that, temporary peer failures can become sticky.
- Pool metadata repair is persisted by only one local node, which reduces races but depends on correct `is_first_cluster_node_local` behavior.
- Decommission resume is delayed and bounded, but it clones cancellation tokens and pool indices into a detached task; shutdown correctness depends on token propagation.
- `ECStore::new` retries `init` with a fixed counter and returns a broad `other` error after exhaustion, so callers lose detailed final-stage error typing.
- Several local disk collection paths use unwrap after checking `is_some`; safe today but sensitive to refactoring.

## Test Signals
The file contains focused unit tests for decommission resume ownership, missing pool/endpoint error messages, retry policy for `ConfigNotFound`, stage error wrapping, cancellable delay behavior, and `pool_first_endpoint_is_local` behavior for expansion pools where the global first endpoint is remote but the new pool's first endpoint is local. These tests cover recent startup/decommission regression boundaries, but no full `ECStore::new` integration test is present.
