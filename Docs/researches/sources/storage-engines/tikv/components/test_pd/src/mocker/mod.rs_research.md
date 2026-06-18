# sources/storage-engines/tikv/components/test_pd/src/mocker/mod.rs

## Purpose
This module defines the extension trait and exports all PD mocker cases used by the `test_pd` server.

## Important APIs, Types, And Functions
`DEFAULT_CLUSTER_ID` is `42`. `Result<T>` is a simple `Result<T, String>` used by mocker overrides. `PdMocker` is a broad trait with default `None` implementations for PD, MetaStorage, and resource-manager RPCs. Returning `None` means the server should try the default service or report unimplemented. Returning `Some(Ok(resp))` sends a response; `Some(Err(err))` becomes a gRPC unknown error in `hijack_unary`.

The trait covers membership, TSO, bootstrap, store/region metadata, splits, cluster config, scatter, GC safe points, service GC safe points, metadata storage, resource-unit metrics, and endpoint injection. It exports `AlreadyBootstrapped`, `Incompatible`, `LeaderChange`, `MetaStorage`, `Retry`, `NotRetry`, `Service`, and `Split`.

## Control Flow And State
This file defines no concrete state beyond constants; it establishes the dispatch contract used by `server.rs`. Default `report_ru_metrics` asserts resource bucket requests are background and then returns `None`, so default service handling can continue or the server can ignore depending on RPC path.

## Risks And Test Signals
Adding new PD RPCs requires extending this trait and `server.rs`; otherwise calls will be unimplemented. The `Option<Result<T>>` dispatch model is compact but easy to misuse: `None` is fallback, not success. Tests should choose narrow mockers to override only behavior under test.
