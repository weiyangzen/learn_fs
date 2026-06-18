# sources/sync-backup/syncthing/lib/relay/client/client.go

## Purpose
Defines the public relay client abstraction and factory that chooses static relay clients or dynamic relay-pool clients by URI scheme.

## Important APIs, Types, and Functions
`RelayClient` embeds `suture.Service` and exposes `Error`, `String`, `Invitations`, and `URI`. `NewClient` accepts a relay URI, TLS certificates, and timeout, returning a static client for `relay` or a dynamic client for `dynamic+http`/`dynamic+https`. `commonClient` wraps `svcutil.ServiceWithError` and the shared invitation channel.

## Control Flow
`NewClient` creates an invitation channel, switches on URI scheme, and constructs the appropriate implementation. `newCommonClient` adapts a `serve(context.Context) error` function into a service and stores the invitation channel.

## State and Persistence Behavior
State is in-memory service error tracking and the invitation channel. No persistence or network I/O occurs in this file; concrete clients perform I/O.

## Dependencies and Integration Points
Depends on TLS, URL handling, relay protocol session invitations, `svcutil`, and `suture/v4`. Used by connection management code that supervises relay services and consumes invitations.

## Risks and Edge Cases
Unsupported schemes return an error. The invitation channel is unbuffered, so concrete client delivery can block if no consumer is receiving. Factory behavior must stay aligned with advertised relay URI schemes.

## Test Signals
Compile-time interface satisfaction is indirect. Runtime tests should create clients for supported and unsupported schemes and verify service error and invitation behavior in concrete implementations.
