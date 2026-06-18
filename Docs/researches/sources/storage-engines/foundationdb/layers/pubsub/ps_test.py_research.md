# sources/storage-engines/foundationdb/layers/pubsub/ps_test.py

Purpose: This interactive Python 2 script is a manual end-to-end test for the pub/sub layer. It creates feeds and inboxes, subscribes them, posts messages, and prints feed and inbox contents.

Important APIs and types: It imports `PubSub` from `pubsub_bigdoc`, uses `fdb.api_version(14)`, opens a hard-coded cluster file/database, and calls `create_feed`, `create_inbox`, `create_subscription`, `post_message`, `print_feed_stats`, `list_inbox_messages`, and `get_feed_messages`.

Control flow: The script clears the entire database, creates three feeds and three inboxes, asserts four subscriptions, posts four messages, prints stats for each feed, lists inbox messages, and iterates messages by one feed.

State and persistence behavior: It destructively deletes all keys with `del db[:]` before seeding pub/sub state. Persistent objects include feed, inbox, subscription, and message records managed by `pubsub_bigdoc`.

Dependencies and integration points: It uses local bindings path manipulation, Python 2 print syntax, and the historical API-version 14. It is closer to a smoke/demo script than an automated test suite.

Risks: Hard-coded `/home/bbc/fdb.cluster` and full database clearing are dangerous outside an isolated test database. It references `pubsub_bigdoc`, while the current listed implementation is `pubsub.py`. Test signals are printed output and assertions for subscription creation, but there are no structured result checks.
