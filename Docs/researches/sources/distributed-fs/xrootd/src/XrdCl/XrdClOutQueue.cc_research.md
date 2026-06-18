# sources/distributed-fs/xrootd/src/XrdCl/XrdClOutQueue.cc

## Purpose

This file implements `OutQueue`, a queue of outgoing messages and their handlers used by connection/postmaster code to buffer, retry, expire, or fail pending sends.

## Important APIs, Types, And Functions

Implemented methods are `PushBack`, `PushFront`, `PopMessage`, `PopFront`, `Report`, `GetSizeStateless`, `GrabExpired`, `GrabStateful`, and `GrabItems`. Each queue item stores a `Message*`, `MsgHandler*`, expiration timestamp, and `stateful` flag.

## Control Flow

Producers push messages at the back or front. Send loops call `PopMessage`, which returns the front message and outputs handler, expiry, and statefulness while removing the item. Failure/cleanup paths call `Report` to notify all queued handlers. Maintenance paths move selected messages from one queue to another: expired items by `expires <= exp`, stateful items by flag, or all items.

## State And Persistence

The queue stores an in-memory `std::list<MsgHelper>`. It does not own persistence. Ownership of message/handler pointers is transferred by queue operations but not deleted by `OutQueue` itself.

## Dependencies And Integration Points

It depends on `XrdClOutQueue.hh` and `XrdClPostMasterInterfaces.hh` for `MsgHandler::OnStatusReady`. It is used by transport/postmaster components managing pending sends, disconnects, and retry behavior.

## Risks

Despite the header comment saying synchronized, this implementation has no internal locking; callers must serialize access. `Report` assumes every item has a non-null handler. `PopFront` on an empty queue is undefined. Expiration comparison treats `expires == exp` as expired and default `exp = 0` will grab items whose expiry is zero. No deletion occurs for items left in a destroyed queue.

## Test Signals

Tests should cover FIFO/LIFO push behavior, pop metadata, stateless counting, expired transfer boundaries, stateful transfer, full transfer, report callback delivery, empty queue behavior under caller guards, and externally synchronized concurrent use.
