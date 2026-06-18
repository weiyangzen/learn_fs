# sources/storage-engines/foundationdb/layers/pubsub/pubsub_orig.py

Purpose: This is an older raw-key prototype of the pub/sub layer. It documents the intended data model and implements feed, inbox, subscription, posting, listing, and feed-stat operations using explicit tuple keys and binary IDs.

Important APIs and types: Key builder functions generate feed, inbox, subscription, watcher, message, and count keys. Transactional internals include `_create_feed_internal`, `_create_inbox_internal`, `_create_subscription_internal`, `_post_message_internal`, `_list_messages_internal`, and `_print_internal`. `PubSub` wraps those with random 64-bit feed/inbox IDs.

Control flow: Feed and inbox creation initialize metadata and count keys. Subscription creation checks existence via count keys, writes inbox subscription and feed subscriber keys, increments counts, and adds the inbox as a watcher. Posting creates a descending global message ID, stores message contents, associates it with the feed, increments the feed message count, and has commented-out watcher dirtying code. Listing scans inbox subscriptions, then each feed's message keys, and loads message bodies.

State and persistence behavior: Persistent state is raw FDB keyspace partitions with prefixes `f`, `i`, and `m`, plus big-endian packed IDs. Counts are manually maintained in separate keys. Watcher/stale-feed state is partly modeled but not fully active in `post_message`.

Dependencies and integration points: It prepends a local bindings path, imports `fdb`, `struct`, `os`, and `sys`, and uses older APIs such as `fdb.tuple_to_key` and `get_range_startswith`. It predates the SimpleDoc implementation.

Risks: The global message ID logic appears inconsistent: it reads `first_greater_than` from `message(0)` but checks `last_key` value at `sys.maxint`, so edge cases are suspect. Dirty watcher propagation is commented out, limiting scalability semantics. Tests should verify ID ordering, counts, subscription existence checks, list output, duplicate subscription idempotence, and missing feed/inbox behavior if this code is still used.
