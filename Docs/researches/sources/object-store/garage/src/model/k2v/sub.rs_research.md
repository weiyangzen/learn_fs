# sources/object-store/garage/src/model/k2v/sub.rs

## Purpose
This file implements in-memory subscription tracking for K2V long polling. It lets local RPC handlers wait for changes to one item or to an entire partition.

## Important APIs, types, and functions
`PollKey` identifies one K2V item by partition and sort key. `PollRange` describes a partition range with optional prefix/start/end. `SubscriptionManager` wraps a mutex-protected `SubscriptionManagerInner` containing item and partition broadcast senders. Methods include `new`, `subscribe_item`, `subscribe_partition`, and `notify`. `PollRange::matches` checks whether an item belongs to a requested range.

## Control flow
Polling code subscribes before or during local reads. Table update hooks call `notify`, which sends a clone of the item to matching item and partition broadcast channels, removing channels that have no receivers. Range poll handlers wait on partition channels until a matching unseen item arrives.

## State and persistence behavior
Subscriptions are transient process-local memory. They are not replicated or persisted; each storage node manages waiters for its local RPC handlers.

## Dependencies and integration points
It depends on `tokio::sync::broadcast`, `std::sync::Mutex`, and K2V item types. `K2VItemTable::updated` calls `notify`, and `K2VRpcHandler` subscribes for poll item/range.

## Risks and edge cases
Broadcast channel capacity is 8, so slow consumers can lag and receive errors; polling code treats `recv` errors as RPC errors. `notify` holds a synchronous mutex while sending; broadcast send is nonblocking but clone cost grows with item size. `PollRange::matches` uses lexicographic string bounds and prefix checks; callers must build start/end consistently.

## Test signals
No direct tests. Coverage should include item and partition subscription delivery, channel cleanup after receivers drop, lag behavior, and range matching with prefix/start/end combinations.
