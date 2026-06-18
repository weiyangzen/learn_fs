# sources/storage-engines/foundationdb/layers/pubsub/remotesend.py

Purpose: This remote benchmark client mixes pub/sub message posting and inbox reads using gevent concurrency. It simulates many clients sending or checking messages against a preloaded user population.

Important APIs and functions: It parses `--zkAddr`, `--database`, `--totalUsers`, `--messages`, and `--threads`, opens FDB with `event_model="gevent"`, constructs `PubSub`, and spawns `message_client` greenlets.

Control flow: Each greenlet sleeps a random initial delay, then loops until it has sent its share of messages. On each iteration it chooses a random user; with 10 percent probability it posts to that user's feed, otherwise it reads that user's inbox. All jobs are joined before printing done.

State and persistence behavior: Persistent state is pub/sub message records and inbox cache/dirty-feed updates. Runtime state is only greenlet counters and random choices.

Dependencies and integration points: It uses gevent monkey patching for threads, local bindings path insertion, Python `random`, and `pubsub_bigdoc`. It expects users already created by `remoteload.py` and subscriptions by `remotesubscribe.py`.

Risks: The message body references `i`, which is the loop variable from greenlet creation and may not be defined as intended inside `message_client` under Python scoping. Integer division of messages by threads can drop remainder messages. Tests should use deterministic seeds, validate total posts, and catch missing-user and scoping errors.
