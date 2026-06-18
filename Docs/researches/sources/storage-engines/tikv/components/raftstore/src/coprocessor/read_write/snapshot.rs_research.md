# sources/storage-engines/tikv/components/raftstore/src/coprocessor/read_write/snapshot.rs

## Purpose
`snapshot.rs` defines the hook for observing raftstore region snapshot creation.

## Important APIs, Types, And Functions
`ObservedSnapshot` is a marker trait requiring `Any + Send + Sync`, allowing concrete snapshot observation payloads to be downcast later. `SnapshotObserver` has `on_snapshot(region, read_ts, sequence_number) -> Box<dyn ObservedSnapshot>`, called when raftstore takes a `RegionSnapshot`.

## Control Flow
`CoprocessorHost::on_snapshot` calls the singleton registered snapshot observer, if present, and returns its boxed observed payload. If no observer is registered, the host returns `None`.

## State And Persistence Behavior
The file stores no state. Implementations may capture snapshot metadata or side data, but this trait only returns an in-memory object. It does not persist snapshot observations by itself.

## Dependencies And Integration Points
Depends on `kvproto::metapb::Region` and `std::any::Any`. It integrates with dispatcher snapshot registration and any subsystem that needs to bind metadata to region snapshots.

## Risks
Only one snapshot observer is supported by the registry, so registrations replace previous observers. Downcasting through `Any` is flexible but shifts type-safety to callers. Implementations run during snapshot creation and must avoid heavy blocking.

## Test Signals
No local tests in this file. Dispatcher behavior for optional singleton snapshot observer should be covered by integration or downstream observer tests.
