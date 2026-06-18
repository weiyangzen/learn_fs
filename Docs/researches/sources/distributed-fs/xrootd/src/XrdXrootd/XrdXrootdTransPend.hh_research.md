# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTransPend.hh

## Purpose

This header declares the pending-transit request node used to bridge delayed xroot responses back to an injected request.

## Important APIs, types, and functions

`XrdXrootdTransPend` stores `next`, `link`, `bridge`, and a union containing either the copied `ClientRequest` or a `short` stream id view. Public methods are `Queue()`, static `Remove()`, and static `Clear()`.

## Control flow

Transit wait-response handling creates a node from the current link, bridge, and request. The node is queued globally. Async response handling removes it by link and stream id, then uses the copied request to restore transit state.

## State and persistence behavior

Nodes are heap-allocated transient state. The static queue is process memory and is mutex-protected in the implementation.

## Dependencies and integration points

The header depends on `XProtocol.hh`, `XrdSysPthread.hh`, `XrdLink`, and `XrdXrootdTransit`. It is used only by transit bridge code.

## Risks and edge cases

The union overlay assumes the stream id occupies the same leading bytes in the copied request representation used by `Remove()`. That should be validated on all supported platforms. Ownership is manual; callers must delete removed nodes or clear them.

## Test signals

Tests should validate stream id matching through the union, lifecycle ownership, and bridge cleanup behavior.
