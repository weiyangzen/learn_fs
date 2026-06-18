# sources/distributed-fs/xrootd/src/XrdCl/XrdClChannelHandlerList.cc

## Purpose

This file implements `XrdCl::ChannelHandlerList`, a small thread-safe helper for managing `ChannelEventHandler` listeners attached to a stream/channel. It supports registering handlers, unregistering handlers, and broadcasting channel events while pruning handlers that ask to be removed.

## Important APIs, types, and functions

`AddHandler(ChannelEventHandler*)` locks `pMutex` and appends the raw handler pointer to `pHandlers`.

`RemoveHandler(ChannelEventHandler*)` locks the same mutex, scans the list for pointer identity, erases the first match, and returns immediately.

`ReportEvent(ChannelEventHandler::ChannelEvent, Status)` locks the list, calls `OnChannelEvent(event, status)` for each handler, and erases handlers that return `false`. Returning `true` keeps the handler registered.

## Control flow

The control flow is deliberately linear. Registration and removal are direct list mutations under `XrdSysMutexHelper`. Event dispatch iterates with an erase-aware iterator so a handler can opt out through its return value without invalidating the traversal.

## State and persistence behavior

State is the in-memory `std::list<ChannelEventHandler*> pHandlers`. No handler is owned by the list, no durable persistence exists, and duplicate registrations are not rejected. If the same pointer is added twice, it receives events twice and `RemoveHandler` removes only the first entry.

## Dependencies and integration points

The implementation includes `XrdClChannelHandlerList.hh` and `XrdClPostMasterInterfaces.hh`. `XrdClStream.hh` contains a `ChannelHandlerList pChannelEvHandlers`, making this helper part of stream event propagation to channel users such as PostMaster, file state handlers, and copy/read code waiting on connection events.

## Risks and edge cases

Handlers are called while `pMutex` is held. If a handler calls back into this list or into code that attempts to register/remove handlers, deadlock is possible unless the broader code avoids that pattern. A slow handler also blocks all list mutations and event delivery.

Because pointers are raw and non-owning, callers must ensure handlers remain alive until removed or until they return `false` from an event. There is no duplicate suppression and no null pointer check.

## Test signals

No direct tests are visible. Useful tests would cover add/remove, self-removal by returning false, duplicate registration behavior, concurrent add/remove/report discipline, and a handler that removes another handler. Stream connection event tests indirectly exercise this helper.
