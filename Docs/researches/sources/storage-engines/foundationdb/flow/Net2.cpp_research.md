# sources/storage-engines/foundationdb/flow/Net2.cpp research

## Purpose

`Net2.cpp` is the concrete, non-simulated Flow network implementation for FoundationDB. It binds the `INetwork` and `INetworkConnections` interfaces to Boost.Asio sockets, TLS contexts, UDP sockets, timers, main-thread task scheduling, DNS resolution, run-loop metrics, slow-task detection, and platform reactor integration. The file is the production path behind `newNet2(...)`, creating a global `N2::Net2` instance that owns the Asio `io_context`, the Flow `TaskQueue`, TLS handshaker side threads, metrics, DNS cache refresh actor, and the state used by `delay`, `yield`, `onMainThread`, `connect`, and `listen`.

## Important APIs, types, and functions

The central type is `N2::Net2 final : public INetwork, public INetworkConnections`. Public methods implement connection creation (`connect`, `connectExternal`, `connectExternalWithHostname`), UDP creation (`createUDPSocket`), listening (`listen`), DNS lookup (`resolveTCPEndpoint*`), scheduling (`delay`, `orderedDelay`, `yield`, `check_yield`, `onMainThread`), lifecycle (`run`, `stop`, `addStopCallback`, `checkRunnable`), and platform services (`getDiskBytes`, `isAddressOnThisHost`, `startThread`, `protocolVersion`, `global`/`setGlobal`).

`Connection` implements plaintext `IConnection` with a `tcp::socket`, nonblocking `read`/`write`, null-buffer readiness probes, and socket setup for `TCP_NODELAY`, optional Linux `TCP_QUICKACK`, and close-on-exec. `SSLConnection` wraps a `tcp::socket` in `boost::asio::ssl::stream`, applies `TLSPolicy`, tracks whether the peer verified, supports client SNI via `connectWithHostname`, and gates TLS handshakes with `networkInfo.handshakeLock` plus client/server throttling maps. `Listener` and `SSLListener` are `IListener` acceptors that construct the corresponding connection type. `UDPSocket` implements `IUDPSocket` for connected or unconnected UDP sockets and exposes `receive`, `receiveFrom`, `send`, `sendTo`, `bind`, `localAddress`, and `native_handle`.

`BindPromise` and `ReadPromise` adapt Boost.Asio callbacks into Flow `Promise`/`Future` results while translating errors to `connection_failed`, `bind_failed`, `address_in_use`, `invalid_local_address`, or `lookup_failed`. `SSLHandshakerThread` is an `IThreadPoolReceiver` used to run blocking TLS handshakes on background threads when configured or when the main-thread handshake pool is saturated. `ASIOReactor` wraps `io_context::run_one`, `poll_one`, and a timer used for sleeping. `SendBufferIterator` adapts Flow `SendBuffer` chains into Boost.Asio `const_buffer` ranges for scatter/gather writes.

## Control flow

Construction initializes Flow globals for metrics, `INetworkConnections`, the Asio service, blob credential files, proxy state, and Linux eventfd when present. `run()` marks the network thread, starts the coordinator DNS refresh actor, optionally starts Flow profiling, and enters a loop until `stopped` becomes true. Each iteration optionally invokes the global run-cycle function, computes sleep time from the task queue, sleeps through the reactor, polls Asio events, updates `currentTime`, processes timers and thread-ready tasks, then executes ready `PromiseTask`s until the queue empties or `check_yield` forces a break. Metrics and starvation trackers are updated around run-cycle, reactor, idle, and task priorities. Stop callbacks and a final simple-counter report run after the loop exits.

Connection control flow is actor-shaped. Plain TCP `Connection::connect` starts `async_connect`, awaits the callback future, then calls `init`; failed or cancelled connects close the socket. `Listener::doAccept` starts `async_accept`, converts the peer endpoint to `NetworkAddress`, calls `Connection::accept`, and returns the connection. TLS uses the same socket accept/connect setup but separates TCP establishment from `connectHandshake`/`acceptHandshake`. The handshake wrappers acquire the shared handshake lock, start either an async main-thread handshake or a blocking side-thread handshake, enforce `CONNECTION_MONITOR_TIMEOUT`, update success/timeout counters, and add failures to throttling state.

DNS lookup is split into `resolveTCPEndpoint_impl`, which owns a local resolver and maps endpoints to Flow `NetworkAddress`, and cache-aware wrappers. `coordinatorDNSCacheRefresh` periodically refreshes or evicts cache entries when `ENABLE_COORDINATOR_DNS_CACHE` is set. `isAddressOnThisHost` probes routing by connecting a temporary UDP socket to the target IP and comparing the selected local endpoint; results are cached and bounded.

## State and persistence behavior

Most state is in-memory runtime state. `Net2` keeps task queues, `currentTime`, TLS policy/context, TLS background actors, DNS cache, address-on-host cache, Flow globals, metric handles, starvation trackers, stop callbacks, and optional blob/proxy configuration. TLS certificate refresh uses `watchFileForChanges` on configured certificate/key/CA paths and replaces `sslContextVar` plus `activeTlsPolicy` after a successful reload, so new TLS connections pick up refreshed credentials. No durable application data is written here; persistent effects are trace logs, metrics, possible TLS file watches, and OS socket/resource state.

The global singleton `N2::g_net2`, thread-local `thread_network`, and Linux profiling globals are process-lifetime state. `stopImmediately` clears queued tasks and marks the network stopped, but intentionally does not perform deep resource cleanup for every process-lifetime object. The DNS and address caches are opportunistic and may be cleared or evicted without persistence.

## Dependencies and integration points

This file depends heavily on Boost.Asio (`io_context`, TCP/UDP sockets, resolver, timers, SSL stream/context), Flow actor/future primitives, `TaskQueue`, `IConnection`, `IUDPSocket`, `IThreadPool`, `TLSConfig`/`TLSPolicy`, `WatchFile`, `ProtocolVersion`, `SendBufferIterator`, `ChaosMetrics`, `TDMetric`, `SimpleCounter`, and `TraceEvent`. It calls platform helpers from `Platform.cpp` for timers, disk bytes, threads, close-on-exec, yielding, and profiling toggles. Network-wide state comes through `g_network->networkInfo`, including TLS throttling maps, metrics, and handshake flow locks.

Integration is broad: storage/server layers call `g_network` methods for scheduling, timers, connections, and listener creation; TLS configuration is supplied at `newNet2`; Swift jobs are optionally enqueued through `_swiftEnqueue`; profiler setup in `Platform.cpp` consumes `net2RunLoopIterations`, `net2RunLoopSleeps`, and the backtrace buffers initialized in this file.

## Risks and edge cases

Run-loop behavior is latency critical. Regressions in `check_yield`, `TaskQueue` ordering, or `reactor.sleep` can starve higher-priority actors or inflate latency. `currentTime` is atomic but many other fields assume network-thread ownership. `onMainThread` is cross-thread and relies on `TaskQueue::addReadyThreadSafe` plus `reactor.wake`; missed wakes can hang callbacks.

TLS behavior has several risk points: handshakes may run on the main thread when side-thread capacity is full, throttling maps must be keyed consistently for client versus server paths, failed handshakes must close sockets without double-completing promises, and certificate reload swaps context/policy for future accepts while existing connections continue with their original context. SNI setup calls both `SSL_set_tlsext_host_name` and hostname verification flags; failures are traced but not explicitly rejected before the handshake result.

Boost.Asio null-buffer readiness probes and nonblocking `read_some`/`write_some` rely on correct translation of `would_block` to zero-byte progress. The code asserts that successful reads/writes send nonzero bytes, so empty buffer chains or unexpected EOF semantics are fatal in debug builds. DNS filtering excludes IPv6 loopback in async resolution but not in the blocking resolver, which is a subtle behavior difference. `isAddressOnThisHost` can log warnings and cache false on routing/socket errors.

## Test signals

Inline tests cover `ThreadSafeQueue` basic behavior, multi-threaded queue ordering, and FIFO behavior for `onMainThread` scheduling. Comments suggest running random unit tests with `fdbserver -r test -f tests/noSim/RandomUnitTests.toml` or `fdbserver -r unittests -f noSim`. Additional useful signals are TLS connect/listen tests, DNS-cache refresh/eviction tests, socket failure injection, noSim latency/slow-task profiling checks, and metrics assertions for `CountReads`, `CountWrites`, `CountYields`, TLS handshake counters, and run-loop callback counters.
