# sources/storage-engines/foundationdb/layers/pubsub/ps_tutorial.py

Purpose: This tutorial script documents the basic pub/sub concepts and walks through creating a feed, an inbox, a subscription, and two messages. It is intended for interactive learning rather than automated validation.

Important APIs and types: It imports `PubSub` from `pubsub_bigdoc`, sets `fdb.api_version(14)`, opens the default database, and uses `create_feed`, `create_inbox`, `create_subscription`, `post_message`, and `get_inbox_messages`.

Control flow: Execution creates Alice's feed and Bob's inbox, subscribes Bob to Alice, posts two messages, and prints messages visible to Bob. The optional database clear is commented out.

State and persistence behavior: The script mutates the default FDB database by adding pub/sub objects and messages. Because it does not clear by default, repeated runs can accumulate or interact with prior tutorial state depending on `pubsub_bigdoc` naming semantics.

Dependencies and integration points: It demonstrates the higher-level pub/sub layer but depends on an older module name and API version. The tutorial text explains feeds, inboxes, and subscriptions inline.

Risks: It is Python 2-era and not isolated. Tests should treat it as documentation; executable checks would need a temporary database/subspace and assertions on returned message lists rather than printed output.
