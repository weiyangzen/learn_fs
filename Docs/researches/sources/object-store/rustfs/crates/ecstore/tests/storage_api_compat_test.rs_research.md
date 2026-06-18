# sources/object-store/rustfs/crates/ecstore/tests/storage_api_compat_test.rs

Purpose: compile-time contract test proving `ECStore` implements public storage traits with expected associated types.

Important APIs and flow: `storage_admin_api_type_name<T>` constrains `T` to `StorageAdminApi<BackendInfo = rustfs_madmin::BackendInfo, StorageInfo = rustfs_madmin::StorageInfo, Disk = DiskStore, Error = Error>`. `storage_api_with_namespace_locking_type_name<T>` constrains `T` to `StorageAPI + NamespaceLocking`. The tests instantiate both helpers with `ECStore` and assert the returned type name ends in `::ECStore`.

State and persistence: no runtime storage state is touched. Trait bounds are the persistent contract.

Dependencies and integration: joins `rustfs_ecstore::{store::ECStore, disk::DiskStore, error::Error, store_api::*}`, `rustfs_storage_api::StorageAdminApi`, and madmin response types. It protects admin/storage trait compatibility used by higher-level object store orchestration.

Risks: type-name string assertions are incidental; the real value is compile-time trait checking. The test does not exercise behavior, associated method semantics, or namespace lock correctness.

Test signals: any trait implementation removal or associated type drift breaks compilation before runtime assertions.
