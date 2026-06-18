# sources/storage-engines/foundationdb/fdbserver/grvproxy/include/fdbserver/grvproxy/GrvProxyServer.h

## Purpose
Public header exposing the GRV proxy server actor entrypoint.

## Important APIs, Types, and Functions
- Forward declares `InitializeGrvProxyRequest` and `ServerDBInfo`.
- Declares `grvProxyServer(GrvProxyInterface, InitializeGrvProxyRequest, Reference<AsyncVar<ServerDBInfo> const>)`.

## Control Flow
Consumers provide the proxy interface, initialization request, and live DB info. The implementation handles readiness, actor composition, and expected termination handling.

## State and Persistence Behavior
No state in the header; runtime state is in `GrvProxyServer.cpp`.

## Dependencies and Integration Points
Includes `GrvProxyInterface` and Flow. This is the public boundary used by worker role startup.

## Risks and Edge Cases
Signature changes affect worker integration. Forward declarations require consistency with implementation includes.

## Test Signals
GRV proxy link tests validate this entrypoint links with component dependencies.
