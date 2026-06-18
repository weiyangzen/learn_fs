# sources/object-store/garage/src/net/lib.rs

## Purpose
This file is the crate root for `garage_net`, a networking library for Garage RPC communication.

## Important APIs, types, and functions
It exports public modules `bytes_buf`, `error`, `stream`, `util`, `endpoint`, `message`, `netapp`, and `peering`, keeps `client`, `recv`, `send`, and `server` private, and re-exports `crate::netapp::*`. Tests are in `test`.

## Control flow
There is no runtime logic in the crate root.

## State and persistence behavior
No state is stored here.

## Dependencies and integration points
Garage RPC and model crates import `NetApp`, node key types, endpoints, messages, priorities, peering manager, and errors through this crate.

## Risks and edge cases
Public/private module boundaries define the crate API. Making send/recv/client internals public or moving re-exports would affect downstream crates.

## Test signals
Crate tests in `net/test.rs` compile through this root. Feature builds with telemetry are also important.
