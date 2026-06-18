# sources/object-store/rustfs/crates/storage-api/src/admin.rs

## Purpose
Defines the admin-facing storage API contract for backend info, storage info, local storage info, disk inventory, and set drive counts.

## Important APIs and Types
`DiskSetSelector` identifies a pool/set pair by `pool_idx` and `set_idx` and has a const constructor. `StorageAdminApi` is an async trait requiring `Send + Sync + Debug`; associated types cover backend info, storage info, disk representation, and error type. Required methods are `backend_info`, `storage_info`, `local_storage_info`, `disk_set_inventory`, and `set_drive_counts`.

## Control Flow and State
The trait defines behavior but stores no state. Implementations own persistence and locking. `disk_set_inventory` returns `Vec<Option<Self::Disk>>`, which can represent missing/offline disks at stable positions.

## Integration Points
Re-exported by `storage-api/src/lib.rs` and intended for storage backends such as `ECStore` to implement while keeping admin consumers decoupled from concrete disk types.

## Risks
Associated return types are unconstrained beyond debug/send/sync/static, so consumers need generic plumbing or adapter types. There are no semantic guarantees about whether info calls are cached or live. `DiskSetSelector` uses raw indexes without validation.

## Test Signals
The test implements a `FakeStorageAdmin` and verifies backend info, storage info, drive counts, and optional disk inventory behavior.
