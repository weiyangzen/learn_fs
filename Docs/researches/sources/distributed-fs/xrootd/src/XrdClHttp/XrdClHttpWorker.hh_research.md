# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpWorker.hh

## Purpose

This header declares `XrdClHttp::CurlWorker`, the worker-thread object that drives libcurl multi handles for queued HTTP operations.

## Important APIs, types, and functions

Public methods include the constructor, deleted copy constructor, `Run`, static `RunStatic`, `Start`, `ClientX509CertKeyFile`, `SetMaintenancePeriod`, and static `GetMonitoringJson`. Private lifecycle methods are `ShutdownAll` and `Shutdown`. `OpStats` tracks per-verb/status counts and durations; `OpKind` classifies metric updates; `OpRecord` records operation statistics.

Static members maintain the global worker list, worker mutex, maintenance period, connection-callout counters, per-verb/status metric array, and vectors pointing to per-worker liveness atomics. Each instance owns the shared queue, continuation queue, active curl operation map, shutdown pipe, startup synchronization, thread object, logger, X.509 credential filenames, and metric offsets.

## Control flow

`XrdClHttpFactory` constructs workers and starts `RunStatic` in threads. `Start` transfers ownership into the static worker list and releases `RunStatic` once the thread object is known. `Run` consumes queued operations, manages curl multi state, and exits on shutdown. Static `initcontrol` handles global curl initialization and all-worker shutdown on plugin unload.

## State and persistence behavior

All state is process-local. Metrics live in static atomics for monitoring and are not persisted unless factory monitoring writes them elsewhere. The worker stores X.509 client cert/key paths read at construction so operations can configure curl handles without rereading environment each time.

## Dependencies and integration points

The header depends on `XrdClHttpOps.hh`, atomics, chrono, mutexes, condition variables, unordered maps, and forward-declared curl/XRootD classes. It is implemented in `XrdClHttpUtil.cc` and constructed by `XrdClHttpFactory.cc`.

## Risks and edge cases

The static worker list owns live worker objects and is also used during shutdown, so lock ordering and thread joins matter. `m_op_map` ties raw curl handles to shared operations and timestamps; any worker change must preserve handle removal/recycling invariants. `m_max_ops` is fixed at 20 per worker while queue size is configurable, which affects backpressure behavior.

## Test signals

Tests should cover startup synchronization, shutdown before/after launch, maintenance-period overrides, monitoring JSON while workers are active, and X.509 cert/key propagation to operations. No direct worker tests were found.
