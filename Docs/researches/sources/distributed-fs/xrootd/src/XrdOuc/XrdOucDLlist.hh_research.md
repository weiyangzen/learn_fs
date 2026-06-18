# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucDLlist.hh

## Purpose
Defines an intrusive circular doubly linked list node template that can also serve as an anchorless list.

## Important APIs, Types, And Functions
`XrdOucDLlist<T>` stores `next`, `prev`, and `item`. Public methods include `Apply`, `Insert`, `Remove`, `Next`, `Prev`, `Item`, `setItem`, and `Singleton`. The destructor removes the node when it appears linked.

## Control Flow
Nodes start as self-referential singletons. `Insert` links a node immediately after the receiver and optionally sets its item. `Remove` unchains and resets the node to singleton. `Apply` traverses from an optional start node or `this`, snapshots the next node before invoking the callback, and stops when the callback returns non-zero.

## State And Persistence
State is in-memory list links and a non-owning `T*` item. The list does not manage item lifetime.

## Dependencies And Integration Points
Header-only utility with no external dependencies. Used by code that needs stable traversal while callbacks may mutate current nodes.

## Risks And Test Signals
Risks include no locking, destructor removal based on `prev != next` missing some corrupted-link states, and caller-owned item lifetime. Test signals are insert/remove order, callback traversal while removing current nodes, singleton detection, and repeated remove/destruct behavior.
