# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucChain.hh

## Purpose
Defines simple template node, stack, and queue containers used by older XRootD utility code where intrusive allocation patterns are preferred.

## Important APIs, Types, And Functions
`XrdOucQSItem<T>` stores `nextelem` and `dataitem`. `XrdOucStack<T>` exposes `Push`, `Pop`, and `isEmpty` over a singly linked LIFO chain. `XrdOucQueue<T>` exposes `Add`, `Remove`, and `isEmpty` over a singly linked FIFO chain with head and tail pointers.

## Control Flow
Callers allocate/wrap items in `XrdOucQSItem`, push/add them, and later pop/remove to retrieve only the `T*`. The container does not delete wrapper nodes during removal; ownership remains with callers.

## State And Persistence
State is only the in-memory anchor/tail pointers. There is no locking, refcounting, or persistence.

## Dependencies And Integration Points
The header has no external includes and is used as a lightweight utility by modules that can manage node lifetime externally.

## Risks And Test Signals
Risks include wrapper leaks, stale node reuse, and no thread-safety. Queue `Remove` returns data without clearing the removed node's `nextelem`, unlike stack `Pop`, so callers should not assume detached nodes are reset. Test signals are basic FIFO/LIFO ordering, empty removal, and lifecycle tests in any owner code that embeds these wrappers.
