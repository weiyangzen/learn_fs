# sources/distributed-fs/xrootd/src/XrdCl/XrdClPoller.hh

## Purpose

This header defines the socket event polling abstraction used by XrdCl channels. It separates transport/channel logic from the concrete polling backend and gives socket handlers a small callback interface for readiness and timeout events.

## Important APIs, Types, And Functions

`SocketHandler` declares event bits `ReadyToRead`, `ReadTimeOut`, `ReadyToWrite`, and `WriteTimeOut`, optional lifecycle hooks `Initialize(Poller*)` and `Finalize()`, required `Event(uint8_t, Socket*)`, and `EventTypeToString`. `Poller` declares lifecycle methods `Initialize`, `Finalize`, `Start`, `Stop`, socket registration/removal, `ShutdownEvents`, read/write notification toggles with timeouts, `IsRegistered`, and `IsRunning`.

## Control Flow

Channels create or receive sockets, register them with a `Poller`, and use `EnableReadNotification`/`EnableWriteNotification` to arm callbacks. Concrete pollers translate OS/backend events into `SocketHandler::Event` calls. `ShutdownEvents` is the non-removal path for suppressing future callbacks before or during teardown.

## State And Persistence Behavior

The header has no state. Implementations are expected to keep socket-to-handler/channel maps and event-arm state. There is no persistence.

## Dependencies And Integration Points

This is consumed by `PollerBuiltIn`, `PostMaster`, and `Channel` code. It depends only on forward declarations for `Socket` and `Poller` plus standard integer/time/string headers.

## Risks And Edge Cases

`EventTypeToString` erases the last character even when no event bits are set, which can underflow on an empty string. Removal semantics warn that `RemoveSocket` may block on backend dispatch loops; callers that need quick callback suppression should use `ShutdownEvents`. Implementers must define timeout behavior consistently because channel retry logic depends on these event bits.

## Test Signals

Tests should verify event bit translation, initialization/finalization order, read/write enable/disable idempotence, callback suppression via `ShutdownEvents`, and behavior for empty/unknown event masks.
