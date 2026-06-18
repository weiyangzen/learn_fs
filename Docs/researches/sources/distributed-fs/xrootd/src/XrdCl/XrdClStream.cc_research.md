# sources/distributed-fs/xrootd/src/XrdCl/XrdClStream.cc

## Purpose

This file implements `XrdCl::Stream`, the postmaster connection/session engine for a server channel. It manages one control socket plus optional data substreams, outgoing and incoming message queues, reconnect logic, stream TTL handling, failure reporting, monitoring, and synchronization between poller callbacks and close operations.

## Important APIs, Types, and Functions

Private helpers include `InMessageHelper`, `SubStreamData`, `SocketDestroyJob`, and `StreamConnectorTask`. `StreamMutex` implements a recursive, callback-aware lock that can abort substream callback lock acquisition while a close is pending. Public behavior is implemented by `Initialize`, `EnableLink`, `Send`, `ForceConnect`, `Finalize`, `Tick`, `OnIncoming`, `OnReadyToWrite`, `OnMessageSent`, `OnConnect`, `OnConnectError`, `OnError`, `ForceError`, timeout handlers, handler registration, incoming-handler installation, `InspectStatusRsp`, `CanCollapse`, and `Query`.

## Control Flow

`Initialize` creates substream 0. `Send` validates session IDs, asks the transport to choose a path, calls `EnableLink`, and queues the message. `EnableLink` either enables the connected uplink or resolves host addresses and starts an async connect. `OnConnect` marks streams connected, assigns a new session for stream 0, creates extra substreams, starts their connects, emits monitor events, and invokes connect handlers. `OnReadyToWrite` moves an item from the out queue into the incoming queue, and `OnMessageSent` finalizes transport accounting and status callbacks. `OnIncoming` routes reconstructed responses through transport handling, close-request handling, partial-response handling, and job-manager dispatch.

Error flow reinserts in-flight helpers when possible, moves peripheral substream work back to stream 0, retries addresses within connection windows, schedules reconnect tasks, and escalates unrecoverable failures via `OnFatalError`. Stream-0 loss resets the session and reports stateful queued work plus incoming handlers as broken.

## State and Persistence Behavior

All state is process-local: URL pointers, preferred URL, transport/poller/task/job managers, `InQueue`, channel data, substream list, resolved addresses, connection windows/retry counters, last fatal error, session ID, byte counters, channel event handlers, and optional data-stream connect job. There is no disk persistence, but session IDs protect stale stateful messages across reconnects.

## Dependencies and Integration Points

The implementation integrates `AsyncSocketHandler`, `Socket`, `Channel`, `TransportHandler`, `OutQueue`, `InQueue`, `JobManager`, `TaskManager`, `Monitor`, `PostMaster`, `XRootDTransport`, and XRootD message utilities. It is central to all networked client operations.

## Risks and Edge Cases

This is concurrency-sensitive code. `SockHandlerClose` replaces handlers while coordinating with poller callbacks; incorrect locking can deadlock or use freed sockets. Retry behavior depends on connection window, retry count, address ordering, and fatal classification. `OnReadTimeout` may destroy the stream/channel through postmaster disconnect, so callers must honor its boolean return. Partial-response and raw-handler paths must reset timeout fences correctly or requests can hang or expire incorrectly.

## Test Signals

Strong signals include connection to multiple resolved addresses, preferred-address collapse behavior, substream fallback to stream 0, stateful-message invalid-session rejection after reconnect, TTL disconnect, stream-broken and fatal-error event delivery, timeout reporting, partial response handling, and cancellation-safe forced disconnects under poller activity.
