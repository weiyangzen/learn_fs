# sources/distributed-fs/xrootd/src/XrdCl/XrdClOutQueue.hh

## Purpose

This header declares `XrdCl::OutQueue`, the outgoing message queue abstraction used to hold messages with their handlers, expiry times, and stateful/stateless retry semantics.

## Important APIs, Types, And Functions

The API includes `PushBack`, `PushFront`, `PopMessage`, `PopFront`, `Report`, `IsEmpty`, `GetSize`, `GetSizeStateless`, `GrabExpired`, `GrabStateful`, and `GrabItems`. `MsgHelper` is the per-item record with `Message* msg`, `MsgHandler* handler`, `time_t expires`, `bool stateful`, and `Reset`.

## Control Flow

Callers enqueue outgoing messages, pop them for transmission, report status to all pending handlers, or move subsets of items between queues based on expiry or statefulness. The queue uses `std::list` so moving/erasing while iterating is straightforward in the implementation.

## State And Persistence

`OutQueue` stores only in-memory list state. It does not own deletion semantics in the declaration; pointer lifetime is governed by the postmaster/transport code using it.

## Dependencies And Integration Points

It includes `<list>`, `<utility>`, and `XrdClXRootDResponses.hh`, and forward-declares `Message` and `MsgHandler`. It integrates with send queues, retry queues, expired queues, and disconnect handling.

## Risks

The "synchronized queue" comment is misleading because no mutex appears in the type. `MsgHelper::Reset` sets a bool to `0`, which works but shows C-style assumptions. Raw pointer ownership is implicit. `PopFront` has no empty check. `GetSize` returns `uint64_t` from `std::list::size`, which is fine but may hide native size type.

## Test Signals

Signals include compile coverage for forward declarations, queue size/is-empty behavior, stateless counting, movement methods preserving item order, status reporting through `MsgHandler`, and thread-safety tests at the caller level rather than inside `OutQueue`.
