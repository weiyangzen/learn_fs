<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/publisher.go -->
# sources/storage-engines/badger/publisher.go

## Purpose
This file implements Badger's update publisher for subscriptions. It tracks subscribers and prefix match rules, batches committed write requests, and delivers matching key/value updates as protobuf `KVList`s.

## Important APIs, Types, And Functions
`subscriber` stores ID, match rules, send channel, closer, and atomic active flag. `publisher` stores a mutex, buffered publication channel, subscriber map, next ID, and trie indexer. APIs include `newPublisher`, `listenForUpdates`, `publishUpdates`, `newSubscriber`, `cleanSubscribers`, `deleteSubscriber`, `sendUpdates`, and `noOfSubscribers`.

## Control Flow
Writers call `sendUpdates`, which increments request refs and queues requests only when subscribers exist. `listenForUpdates` drains one or more queued request batches with `slurp`, then calls `publishUpdates`. Publishing locks the subscriber/index state, builds per-subscriber `KVList`s by matching each entry key against the trie, copies key/value bytes, strips timestamps from keys, includes version and expires-at, and sends to active subscribers. Cleanup removes trie matches, deletes subscribers, and signals subscriber closers.

## State And Persistence Behavior
Publisher state is in-memory only. It does not affect DB durability, but it must respect request reference counting: `publishUpdates` decrements refs after delivering. Delivered `KV` values are safe copies of committed entries and include version metadata parsed from internal keys.

## Dependencies And Integration Points
It depends on `pb.KVList`, `pb.Match`, the trie matcher, `requests` refcounting, `Entry`, key parsing helpers in `y`, and `z.Closer`. It backs the DB subscription API and is fed by the write path after commits.

## Risks And Edge Cases
Publishing holds the mutex while sending to buffered subscriber channels; full subscriber channels can block all publishing while the lock is held. `newSubscriber` inserts the subscriber before adding all matches, so an `AddMatch` error can leave partial state unless callers handle cleanup. The active flag is checked before send but deletion/close races require careful ordering. Batching preserves queue order but coalesces multiple request slices into one publish pass.

## Test Signals
`publisher_test.go` covers a previous deadlock scenario, delivery ordering for sequential writes, and multiple prefix subscriptions. Tests focus on liveness and ordering rather than channel backpressure or partial match-add errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/publisher.go -->
