# sources/storage-engines/tikv/components/sst_importer/src/caching/storage_cache.rs

Purpose: adapts `CacheMap` to cache pools of external storage clients for a `StorageBackend`.

Important APIs and types: `StorageBackendFactory` holds a protobuf `StorageBackend` and `BackendConfig`, implements `MakeCache`, and creates a `StoragePool`. `StoragePool` stores boxed `Arc<dyn ExternalStorage>` clients and implements `ShareOwned` by returning a randomly selected storage client.

Control flow: `StoragePool::create` creates `size` external-storage clients with cloned backend config, supports failpoint `create_storage_slowly`, and returns the pool. `get` chooses a random index. `Debug` prints the URL of a selected storage or `<unknown>`.

State and persistence behavior: process-local cacheable storage clients only. No direct file writes. Failpoint may simulate slow/failing creation.

Dependencies and integration points: used by SST importer external storage cache. Depends on `external_storage`, `kvproto::brpb::StorageBackend`, `rand`, failpoints, and importer `Error`.

Risks: random selection assumes the pool is non-empty; current factory uses size 16. Creation failure of any one client fails the whole pool. URL in debug uses a random member and can vary between logs.

Test signals: covered indirectly through `CacheMap` tests and importer external-storage tests outside this subset.
