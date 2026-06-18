# sources/object-store/garage/src/net/endpoint.rs

## Purpose
This file defines typed RPC endpoints over `NetApp`. It maps application message types and handler objects to path-addressed local handlers and remote calls, with support for attached request/response streams.

## Important APIs, types, and functions
`StreamingEndpointHandler<M>` handles full `Req<M>` and returns `Resp<M>`. `EndpointHandler<M>` is the simpler message-only trait, with a blanket implementation into streaming handling. `Endpoint<M,H>` stores path, owning `NetApp`, and optional handler in `ArcSwapOption`. Public methods are `path`, `set_handler`, `call_streaming`, and `call`. Internal `GenericEndpoint`, `DynEndpoint`, and `EndpointArc` erase endpoint types for dispatch from server connections.

## Control flow
Local calls bypass serialization and invoke the handler directly when target equals local node ID. Remote calls find a `ClientConn` by target node ID, serialize the request, and call over the connection. Incoming encoded requests are decoded by `EndpointArc::handle`, passed to the registered handler, encoded as `RespEnc`, or fail with `NoHandler`.

## State and persistence behavior
Endpoint state is in-memory handler registration. `drop_handler` clears references during shutdown to break cycles. No persistence.

## Dependencies and integration points
It depends on `arc-swap`, futures boxed futures, message encoding, netapp connection maps, and network errors. `NetApp::endpoint` registers endpoints in a path map; server connections use `GenericEndpoint` dispatch.

## Risks and edge cases
The unit handler `()` panics if it receives a request, so client-only endpoints must not be exposed to incoming traffic. `NetApp::endpoint` panics on duplicate paths. Local calls skip serialization, which is efficient but means serialization errors are only observed on remote paths. Handler absence maps to `NoHandler`.

## Test signals
Network tests should cover local and remote endpoint calls, no-handler errors, streaming handlers, and duplicate endpoint path panics.
