# sources/distributed-fs/xrootd/src/XrdCl/XrdClChannelHandlerList.hh

## Purpose

This header declares `XrdCl::ChannelHandlerList`, a mutex-protected list of `ChannelEventHandler` observers. It is a compact utility used by stream/channel code to centralize event listener management.

## Important APIs, types, and functions

`AddHandler`, `RemoveHandler`, and `ReportEvent` are the complete public surface. `ReportEvent` accepts a `ChannelEventHandler::ChannelEvent` and a `Status`, matching the interface declared in `XrdClPostMasterInterfaces.hh`.

The private state is `std::list<ChannelEventHandler*> pHandlers` and `XrdSysMutex pMutex`.

## Control flow

Callers add handlers before they need event notification, remove them when no longer interested, and stream/channel code calls `ReportEvent` when a channel event occurs. The implementation decides whether handlers stay subscribed based on `OnChannelEvent`'s boolean return.

## State and persistence behavior

The class stores only non-owning handler pointers. It does not persist state, transfer ownership, or define copy semantics. Since no copy constructor is deleted in the header, accidental copying would copy raw pointers and mutex state if allowed by the compiler/toolchain, but typical `XrdSysMutex` semantics should make copying unavailable or unsafe.

## Dependencies and integration points

The header depends on `<list>`, `XrdClPostMasterInterfaces.hh`, `XrdClStatus.hh`, and `XrdSysPthread.hh`. Its principal integration is as a member of `Stream`, where it connects low-level socket events to higher-level clients.

## Risks and edge cases

The header does not document ownership, duplicate policy, or callback locking semantics; those are important because the implementation calls handlers under lock. It also does not prevent null handlers or repeated insertion.

## Test signals

No direct tests are included. Compile-time coverage comes from `XrdClStream` and channel users. Runtime signals should focus on handler lifecycle, event ordering, and deadlock avoidance.
