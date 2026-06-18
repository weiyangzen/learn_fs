# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTransPend.cc

## Purpose

This file implements the global pending-request queue used by `XrdXrootdTransit` for `kXR_waitresp` bridge operations. It stores a request until an asynchronous attention response arrives.

## Important APIs, types, and functions

`Queue()` pushes an item onto `rqstQ`. `Remove(XrdLink*, short sid)` removes the first matching pending request by link and stream id. `Clear(XrdXrootdTransit*)` deletes all pending requests owned by a transit object. Static state is protected by `myMutex`.

## Control flow

When a bridged request receives `waitresp`, transit code allocates `XrdXrootdTransPend`, copies the request, and queues it. Later `XrdXrootdTransit::Attn()` calls `Remove()` with the link and stream id from the attention response; if found, transit resumes using the stored request. Recycle/disconnect calls `Clear()` to avoid dangling pending work.

## State and persistence behavior

The queue is process memory only. Each node owns a copied `ClientRequest` and borrowed link/bridge pointers. There is no timeout in this file; lifetime is controlled by attention arrival or bridge cleanup.

## Dependencies and integration points

It depends on protocol wire structs, `XrdSysMutex`, `XrdLink`, and `XrdXrootdTransit`. It is tightly coupled to `XrdXrootdResponse::Send()` async attention routing.

## Risks and edge cases

The queue is a simple LIFO singly linked list and linear search; many pending waitresp requests could make attention delivery O(n). Matching uses a `short` stream id view over the two stream bytes, so byte-order consistency with the sender is essential. If attention never arrives and cleanup is missed, entries leak until transit recycle.

## Test signals

Tests should cover queue/remove order, non-matching link or stream id, clear-by-bridge, concurrent queue/remove, and attention after recycle.
