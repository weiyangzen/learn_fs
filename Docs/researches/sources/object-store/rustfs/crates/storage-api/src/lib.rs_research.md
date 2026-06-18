# sources/object-store/rustfs/crates/storage-api/src/lib.rs

## Purpose
Crate root for storage API contracts.

## Important APIs
Declares modules `admin`, `bucket`, and `error`, then re-exports `DiskSetSelector`, `StorageAdminApi`, bucket DTOs, `StorageErrorCode`, and `StorageResult`.

## Control Flow and Integration
No runtime logic. The root acts as the public facade for storage consumers and implementations.

## Risks and Test Signals
Re-export changes are semver-sensitive. Tests are in submodules.
