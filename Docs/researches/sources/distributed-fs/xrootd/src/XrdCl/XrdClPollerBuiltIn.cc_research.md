# sources/distributed-fs/xrootd/src/XrdCl/XrdClPollerBuiltIn.cc

## Purpose

This file implements `PollerBuiltIn`, the concrete `Poller` backed by `XrdSys::IOEvents::Poller` and `IOEvents::Channel`. It manages multiple poller threads, socket registration, event callback translation, read/write notification state, and safe callback shutdown.

## Important APIs, Types, And Functions

Private `PollerHelper` stores an IOEvents channel, callback, enabled flags, and timeouts. Private `SocketCallBack` translates IOEvents flags to `SocketHandler` flags and invokes the user handler. Its nested `DisableControl` coordinates `ShutdownEvents` with in-flight callbacks. `PollerBuiltIn` implements lifecycle, `AddSocket`, `RemoveSocket`, `ShutdownEvents`, read/write notification toggles, `IsRegistered`, `GetNextPoller`, `RegisterAndGetPoller`, `UnregisterFromPoller`, `GetPoller`, and `GetNbPollerInit`.

## Control Flow

`Start` creates `pNbPoller` backend pollers, initializes round-robin state, and reattaches any sockets stored while stopped, re-enabling saved read/write notifications. `AddSocket` validates status, assigns a backend poller by file descriptor, creates a callback/channel, calls `handler->Initialize(this)`, and stores the helper. Notification methods update helper state and enable/disable backend channel event masks if a backend poller exists. `Stop` stops and deletes backend pollers, clears fd-to-poller mappings, disables/deletes live channels, and leaves helper registration state for a later `Start`. `Finalize` deletes remaining helpers and callbacks.

## State And Persistence Behavior

State is in-memory: `pSocketMap` maps `Socket*` to helper objects, `pPollerMap` maps file descriptors to backend pollers, `pPollerPool` owns backend pollers while running, and `pNext` implements round-robin assignment. `pMutex` protects those structures. No state persists across process lifetime.

## Dependencies And Integration Points

The implementation uses `XrdSysIOEvents`, `XrdSysPthread`, `XrdSysE2T`, `DefaultEnv`, `Env`, `Log`, `Constants`, `Socket`, and optimizer macros. It is created by `PollerFactory` and owned by `PostMaster`.

## Risks And Edge Cases

Callback teardown is delicate: handlers may remove their own socket during `Event`, so `SocketCallBack` saves the control object before invoking the handler. `ShutdownEvents` waits unless called from the same callback thread. `Stop` and `RemoveSocket` unlock while stopping/deleting backend objects, so concurrent channel operations must follow poller locking expectations. Backend creation failure after some pollers are created returns false without cleaning already-created pollers in that path. `EventTypeToString` inherited empty-mask risk can be triggered by backend flags that map to no known bits.

## Test Signals

Tests should register sockets, enable/disable notifications, simulate callback self-removal, call `ShutdownEvents` during an in-flight callback, stop/start with registered sockets, and verify multiple sockets are assigned round-robin across configured `ParallelEvtLoop` pollers.
