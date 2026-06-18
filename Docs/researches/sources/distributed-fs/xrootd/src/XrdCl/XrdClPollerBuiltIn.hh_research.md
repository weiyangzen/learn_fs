# sources/distributed-fs/xrootd/src/XrdCl/XrdClPollerBuiltIn.hh

## Purpose

This header declares the built-in XrdCl poller implementation. It adapts the generic `Poller` interface to XRootD's internal IOEvents pollers and supports multiple event-loop threads.

## Important APIs, Types, And Functions

`PollerBuiltIn` overrides all `Poller` methods: lifecycle, socket registration/removal, callback shutdown, read/write notification toggles, registration checks, and `IsRunning`. Private helpers select/associate backend pollers: `GetNextPoller`, `RegisterAndGetPoller`, `UnregisterFromPoller`, `GetPoller`, and `GetNbPollerInit`. Type aliases define `PollerMap`, `SocketMap`, and `PollerPool`.

## Control Flow

Construction initializes `pNbPoller` from the environment via `GetNbPollerInit`. Public calls delegate to implementation logic in the `.cc` file while shared structures are protected by `pMutex`.

## State And Persistence Behavior

The object owns socket-helper registrations and backend poller pointers while active. `IsRunning` is defined as non-empty `pPollerPool`. State survives `Stop` enough to permit restart with previous registrations, but not process persistence.

## Dependencies And Integration Points

The header depends on `XrdSysPthread`, `XrdClPoller`, and forward declarations for `XrdSys::IOEvents::Poller` and `AnyObject`. It is the only built-in implementation registered by `PollerFactory`.

## Risks And Edge Cases

Socket maps use raw `Socket*` keys and raw helper pointers, so ownership/lifetime must be managed externally by channels. The class assumes file descriptors uniquely identify backend-poller assignment while registered. Restart behavior depends on helper flags matching backend channel state.

## Test Signals

Compile and lifecycle tests should verify that all virtual methods are implemented, `IsRunning` tracks backend pool state, and configured `ParallelEvtLoop` values affect `pNbPoller`.
