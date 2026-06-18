# sources/distributed-fs/xrootd/src/XrdCl/XrdClStream.hh

## Purpose

This header declares the stream/session abstraction and its specialized mutex. It defines how postmaster code sends messages over multiplexed sockets and receives connection, response, timeout, and error callbacks from socket handlers.

## Important APIs, Types, and Functions

`StreamMutex` exposes regular locking, substream-aware locking, deferred close-function locking, and close notifications. `StreamMutexHelper` is the RAII wrapper. `Stream` declares status values, dependency setters, `Initialize`, `Send`, `EnableLink`, `Finalize`, `Tick`, `ForceConnect`, substream callbacks, error callbacks, event-handler management, incoming-handler install/inspection, data-stream on-connect hooks, `CanCollapse`, `Query`, and channel lifetime access.

## Control Flow

Callers construct a stream for a URL, inject transport, poller, queues, task/job managers, and channel data, then call `Initialize`. `Send` and `EnableLink` are the outbound entry points. The `AsyncSocketHandler` calls back into `OnConnect`, `OnReadyToWrite`, `OnMessageSent`, `OnIncoming`, and timeout/error methods. Private helpers handle partial responses, address matching, requeueing failed in-flight work, monitoring disconnects, request-close follow-up, and socket-handler replacement.

## State and Persistence Behavior

The header defines the state held by a stream: URL identity, transport dependencies, mutex, queue dependencies, channel data, retry/error windows, substreams, resolved addresses, network-stack choice, session ID, monitoring timestamps/byte counters, optional on-data-connect job, and weak owning channel reference. It is nonpersistent and tied to channel lifetime.

## Dependencies and Integration Points

It depends on poller, status, URL, postmaster interfaces, channel event handlers, job manager, in queue, utility/network types, atomics, pthread IDs, and transport/message classes. It is the primary integration contract between `Channel`, `AsyncSocketHandler`, `TransportHandler`, and queue managers.

## Risks and Edge Cases

The header documents a subtle lock contract: close must wait for poller callbacks unless running inside the callback thread, and callback lock acquisition can be aborted. Implementers must preserve this behavior when adding callbacks. Public callbacks are callable from poller/job contexts, so ownership and unlock-before-report patterns are critical.

## Test Signals

Header-level coverage should be indirect: compile-time API compatibility, stream lifecycle integration tests, lock stress tests around close and callbacks, and query/event-handler behavior through postmaster/channel tests.
