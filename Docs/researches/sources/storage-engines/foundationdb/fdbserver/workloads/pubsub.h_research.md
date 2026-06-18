# sources/storage-engines/foundationdb/fdbserver/workloads/pubsub.h

## Purpose
`pubsub.h` declares a simple FoundationDB-backed pub/sub abstraction used by workload code. Its header comment explains the intended data model and operational assumptions for feeds, inboxes, messages, watcher lists, stale lists, and inbox caches.

## Important APIs, Types, and Functions
The file aliases `Feed`, `Inbox`, and `MessageId` to `uint64_t`. `Message` contains `originatorFeed`, `messageId`, and arena-backed `data`, and provides a serializer. `PubSub` owns a `Database` handle and exposes asynchronous methods to create feeds and inboxes, create subscriptions, post messages, and list feed or inbox messages.

## Control Flow
The header itself contains no implementation, but it defines the expected flow: posting appends a message to a feed and marks watcher inboxes dirty; listing inbox messages updates dirty feed caches and merges recent messages from subscribed feeds. `cursor` defaults to `0` for list calls, matching the implementation's descending/global id scheme.

## State and Persistence Behavior
No state is stored in the header except the `Database cx` member. The declared API implies all persistent state is externalized to FDB key ranges managed by `pubsub.cpp`. `Message::data` is a `Standalone<StringRef>`, so returned messages carry their arena lifetime with the value bytes.

## Dependencies and Integration Points
It includes `fdbclient/NativeAPI.actor.h` for `Database`, `Future`, `Standalone`, and `StringRef`. It is consumed by `pubsub.cpp` and any workload or test code that wants a compact pub/sub API.

## Risks and Edge Cases
The model assumes retroactive subscriptions and warns that paging can look odd when subscriptions are added during reads. There are no explicit namespaces or include guards in this header, which relies on project include patterns and can be fragile if included repeatedly.

## Test Signals
No tests are defined in the header. Testability comes through the asynchronous `PubSub` API and message serialization round trips.
