<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/object-capacity/src/capacity_scope.rs -->
# sources/object-store/rustfs/crates/object-capacity/src/capacity_scope.rs

## Purpose
Provides temporary disk-scope propagation for capacity refreshes. Storage/write-side code can associate affected disks with a `Uuid` token, and the capacity manager later consumes that token to mark only those disks dirty. It also supports a global dirty scope queue for paths that cannot pass a token directly.

## Important APIs, Types, and Functions
`CapacityScopeDisk` identifies a disk by `endpoint` and `drive_path`. `CapacityScope` is a vector of those disk keys. `record_capacity_scope` stores or merges a scope for a token. `take_capacity_scope` removes and returns a scope if it has not expired. `record_global_dirty_scope` adds disks to a global `HashSet`, and `drain_global_dirty_scopes` atomically drains that set. Internal helpers include TTL pruning, hard-limit eviction by oldest timestamp, and duplicate-aware scope merging.

## Control Flow
The token registry is lazily initialized with `OnceLock<Mutex<HashMap<Uuid, CapacityScopeEntry>>>`. New token records trigger pruning only after the soft limit and enforce the hard limit by evicting oldest entries. Repeated records for the same token merge unique disks and refresh `recorded_at`. Taking a token removes it first, then rejects stale entries older than five minutes.

## State and Persistence
All state is process-local memory. The token registry has a soft limit of 2,048 and hard limit of 4,096 entries; both protect against unbounded leak when write scopes are never consumed. Global dirty scopes are a set, so duplicate disk records collapse.

## Dependencies and Integration
Depends only on std collections/synchronization and `uuid`. It is consumed by `capacity_manager` for scoped dirty tracking and by write paths that can record capacity-impacting disk scopes.

## Risks
TTL is based on `Instant`, so delayed consumers silently lose stale scope and fall back to unscoped behavior. HashSet ordering means drained global dirty scopes are nondeterministic. A poisoned mutex is recovered with `into_inner`, which keeps the service running but may retain partially mutated state.

## Test Signals
Tests cover record/take round trips, one-time token consumption, merging duplicate disks for a token, hard-limit enforcement, poison recovery for both registries, global dirty scope deduplication, and drain semantics.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/object-capacity/src/capacity_scope.rs -->
