# sources/storage-engines/foundationdb/fdbserver/workloads/pubsub.cpp

## Purpose
`pubsub.cpp` implements the storage and transactional behavior for a small FoundationDB-backed pub/sub model declared in `pubsub.h`. It provides feeds, inboxes, subscriptions, message posting, inbox cache maintenance, and feed/inbox message listing.

## Important APIs, Types, and Functions
The exported methods are `PubSub::createFeed`, `createInbox`, `createSubscription`, `postMessage`, `listInboxMessages`, and `listFeedMessages`. Helper key builders create lexicographic key families for inboxes, subscriptions, stale feeds, inbox caches, feeds, subscribers, feed messages, watchers, global messages, and dispatch entries. `uInt64ToValue` and `valueToUInt64` encode ids as fixed-width hex strings. Core actors include `_createFeed`, `_createInbox`, `_createSubscription`, `_postMessage`, `updateFeedWatchers`, `singlePassInboxCacheUpdate`, `updateInboxCache`, `getFeedLatestAtOrAfter`, `getMessage`, `_listInboxMessages`, and `_listFeedMessages`.

## Control Flow
Creation methods pick random ids and retry transactions until an unused feed or inbox key is found. Subscription creation validates both endpoints, updates inbox and feed indexes, increments counters, and registers the inbox as a watcher on the feed. Posting first reserves a decreasing global message id and dispatch entry, then in a second transaction updates feed message indexes, stale inbox markers for all watchers, the message payload, and clears the dispatch marker. Inbox listing refreshes stale feed cache entries, reads cached per-feed latest messages, adjusts for the pagination cursor, checks dispatch entries for ordering gaps, and merges feed streams by message id.

## State and Persistence Behavior
All state lives in FDB keys using textual prefixes. Feeds store metadata, subscriber count, message count, latest message id, per-feed message ids, subscribers, and watchers. Inboxes store metadata, subscription count, subscription keys, stale-feed markers, cache-by-message-id, and cache-by-feed entries. Global message ids are assigned in reverse order so smaller keys represent newer messages.

## Dependencies and Integration Points
The file depends on `NativeAPI.actor.h`, `Transaction`, `RangeResult`, `TraceEvent`, actor retries with `tr.onError`, and the types from `pubsub.h`. It is a workload/demo component rather than a production FDB subsystem.

## Risks and Edge Cases
The implementation contains several "SOMEDAY" notes: id allocation is random instead of atomic, global ordering is only approximated, and frequently updated feeds can cause repeated stale-cache passes. There is a likely key bug in `_createSubscription`: it writes `keyForFeedSubscriberCount(inbox)` instead of `keyForFeedSubscriberCount(feed)` when incrementing feed subscriber count. Several `.get()` calls assume count/latest keys exist once metadata exists.

## Test Signals
There are no local unit tests in this file. Runtime signals are trace events such as `PubSubCreateFeed`, `PubSubCreateInbox`, `PubSubCreateSubscription`, `PubSubPost`, `PubSubListInbox`, and `PubSubListFeed`; correctness is otherwise observable through API return values and stored key consistency.
