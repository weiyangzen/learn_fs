# sources/storage-engines/tikv/components/raftstore/src/store/worker/mod.rs

## Purpose
This module declares raftstore worker submodules and re-exports their public runner/task types and key helper types. It is the public facade for background workers used by raftstore construction and scheduling.

## Important APIs, Types, and Functions
- Private submodules include check leader, cleanup, cleanup snapshot/SST, compact, consistency check, disk check, PD, raft log GC, local read, refresh config, region, snapshot generation, split check/config/controller/validator.
- Public module: `metrics`.
- Re-exports include `CheckLeaderRunner/Task`, `CleanupRunner/Task`, `CompactRunner/Task`, `FullCompactController`, `ConsistencyCheckRunner/Task`, `DiskCheckRunner/Task`, PD reporting types, raftlog GC types, local read types, refresh config types, region worker types, snapshot generation types, split check/config/controller types, and `SplitValidator`.

## Control Flow
There is no runtime control flow in this file. Compile-time module declarations determine which worker implementations are included, and `pub use` blocks define the external import surface for other raftstore modules.

## State and Persistence Behavior
The module itself has no state and no persistence effects. It shapes access to workers that do hold engine handles, routers, metadata references, metrics, and filesystem-backed components.

## Dependencies and Integration Points
It integrates all sibling worker files into `crate::store::worker`. Store/bootstrap code can import a stable facade rather than each concrete submodule path. It also exposes constants and helper types from split and snapshot generation workers that are needed outside their implementation modules.

## Risks and Edge Cases
Because most submodules are private, removing or renaming a re-export can break downstream raftstore code even when the implementation remains. The facade mixes many domains, so accidental visibility changes may widen or shrink APIs unexpectedly.

## Test Signals
There are no direct tests. The signal is compile-time: if a worker module, type alias, or re-export is wrong, dependent raftstore modules fail to compile. Runtime behavior is covered by the individual worker modules.
