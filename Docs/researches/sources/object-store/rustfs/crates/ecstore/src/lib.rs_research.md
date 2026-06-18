# sources/object-store/rustfs/crates/ecstore/src/lib.rs

Purpose: This is the ecstore crate root. It declares the crate's public module tree, hides selected implementation modules, and re-exports key global and storage traits for downstream crates.

Important APIs and types: Public modules include admin, batch processing, bitrot, bucket, cache, compression, config, data usage, disk, layout, endpoints, erasure coding, error, global, realtime metrics, notification system, pools, rebalance, RIO, RPC, set-disk, store, store API, list objects, store utils, client, event, event notification, and tier. Private modules include `data_movement`, `sets`, and `store_init`. Re-exports include `set_global_endpoints`, `update_erasure_type`, lock-client getters/setters, `new_object_layer_fn`, `resolve_object_store_handle`, `set_object_store_resolver`, `GLOBAL_Endpoints`, and `StorageAPI`.

Control flow: There is no runtime control flow outside test code. The crate root determines which modules compile into the public API and which names are available from `rustfs_ecstore::*`.

State and persistence behavior: The file owns no state. It exposes stateful global APIs from `global.rs`.

Dependencies and integration points: The module declarations bind together the ecstore object-store stack. The event, metrics, notification, error, and global files in this work item are all public modules through this root. The `rio_tests` module checks feature-selected backend identity via `crate::rio::backend_name()`.

Risks: `#![allow(dead_code)]` at the crate root can hide unused public or private scaffolding, including partial event-notification structures. Public module declarations are compatibility commitments; renaming or privatizing modules affects external crates. Feature-dependent RIO behavior is guarded only by a small backend-name test here.

Test signals: The root-level test `uses_expected_rio_backend` asserts that the selected RIO backend name matches the `rio-v2` feature flag. Broader compile and integration tests validate module visibility and re-export correctness.
