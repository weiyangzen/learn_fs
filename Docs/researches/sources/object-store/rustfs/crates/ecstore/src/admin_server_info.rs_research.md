# sources/object-store/rustfs/crates/ecstore/src/admin_server_info.rs

Purpose: builds admin/server information responses for local and cluster RustFS nodes, including network status, storage disks, data usage, backend erasure layout, pool/set statistics, and deployment/build metadata.

Important APIs and functions: `is_server_resolvable` pings a remote node service with a signed Tonic client and flatbuffer `PingBody` under a one-second timeout. `get_local_server_property` builds `ServerProperties` from global endpoints, boot time, object store state, network reachability, and local storage info. `get_server_info` merges notification-system remote server info with local properties and usage/backend summaries. Helpers compute online/offline disk stats, pool info, and commit ID.

State and persistence: reads global singletons (`GLOBAL_Endpoints`, `GLOBAL_BOOT_TIME`, object store handle, notification sys, deployment ID), loads data usage cache/backend data, and inspects storage admin state. It does not mutate persistent state.

Dependencies and integration points: integrates `rustfs_madmin` response models, `StorageAdminApi`, data usage cache, node RPC/Tonic signing, flatbuffers, shadow build metadata, and heal drive states.

Risks: server info can block on remote ping and backend usage calls; warnings indicate timing diagnostics. Disk online/offline classification treats root disks specially and can underflow if counts become inconsistent. Pool indexing assumes disk-reported indexes align with `store.pools`.

Test signals: unit test verifies `get_server_info(false)` includes global deployment ID. Broader behavior relies on integration/admin API tests.
