# sources/storage-engines/tikv/components/test_pd/src/util.rs

## Purpose
This file provides helper constructors for PD RPC clients pointed at mock PD server endpoints.

## Important APIs And Functions
`new_config` converts `(host, port)` tuples into a `pd_client::Config` endpoint list. `new_client` and `new_client_v2` build `RpcClient` and `RpcClientV2` using either a provided `SecurityManager` or a default insecure one. `new_client_with_update_interval` and `new_client_v2_with_update_interval` also override the client's PD membership update interval.

## Control Flow And State
The helpers are pure constructors except for allocating a default `SecurityManager`. They unwrap client creation, so construction failures are test failures.

## Integration Points And Risks
They integrate with `pd_client::{RpcClient, RpcClientV2, Config}`, `security`, and `ReadableDuration`. Endpoint strings are formatted as `host:port` without URI schemes. Tests that need TLS must pass a configured security manager.

## Test Signals
These utilities are validated indirectly by tests that start `test_pd::Server`, call `bind_addrs`, and construct clients with the returned addresses.
