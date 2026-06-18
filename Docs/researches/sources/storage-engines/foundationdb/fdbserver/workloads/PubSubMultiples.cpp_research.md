## sources/storage-engines/foundationdb/fdbserver/workloads/PubSubMultiples.cpp

`PubSubMultiplesWorkload` appears to be a scaffold for exercising many pub/sub feeds and inboxes per actor, but only node creation is implemented. It creates `inboxesPerActor` feeds and inboxes for each actor and stores their numeric IDs under deterministic `/PSM/feeds/<offset>` and `/PSM/inbox/<offset>` keys.

Important APIs are `PubSub::createFeed`, `PubSub::createInbox`, `Transaction`, `PerfIntCounter`, and tester actor scheduling. `keyForFeed`, `keyForInbox`, and `valueForUInt` define the persisted mapping from actor/client offsets to pub/sub object IDs.

Setup calls `createNodes`, which starts one `createNodeSwath` per actor on cloned databases. Each swath creates feed/inbox pairs and commits their IDs in a retry loop. `start` launches `startTests` in a local future and returns `delay(testDuration)`. `startTests` waits for `createSubscriptions` futures and starts `messageSender`, but both are stubs returning `Void`; no subscriptions or messages are actually created.

Persistent state is the created pub/sub metadata plus the `/PSM` mapping keys. Runtime message metrics are defined but never incremented. Risks are mostly incompleteness: offset calculation uses `clientId * clientCount * actorCount * inboxesPerActor`, which looks suspicious for multi-client uniqueness, and the workload reports success despite no validation. It may still serve as a setup stressor for pub/sub object creation.

Integration points are the `pubsub.h` helper layer and FDB transactions. Test signals are limited to successful setup and the `PSMNodesCreated` trace; `check` returns true and `Messages` remains zero unless future code fills in sender/subscriber behavior.
