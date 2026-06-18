# sources/storage-engines/foundationdb/layers/pubsub/remotesubscribe.py

Purpose: This command-line utility creates random follower subscriptions among preloaded pub/sub users. It is part of the remote pub/sub benchmark setup.

Important APIs and functions: It parses `--zkAddr`, `--database`, `--totalUsers`, and `--followers`, opens the remote database, constructs `PubSub`, and calls `create_subscription(get_feed_by_name(...), get_inbox_by_name(...))`.

Control flow: For each follower edge, it chooses two random user IDs between zero and `totalUsers`; if they differ, it subscribes the second user's inbox to the first user's feed. Progress is printed every 100 attempted edges.

State and persistence behavior: Persistent state is subscription records and any dirty-feed/watch state maintained by `pubsub_bigdoc`. Duplicate random pairs are possible and self-pairs are skipped, so the final edge count can be less than `followers`.

Dependencies and integration points: It uses argparse, local binding path insertion, Python `random`, and `pubsub_bigdoc`. It expects users to exist in the same zero-padded name format created by `remoteload.py`.

Risks: `random.randint(0, args.totalUsers)` includes `totalUsers`, while `remoteload.py` creates up to `userCount - 1`, so the script can reference a non-existent user. Tests should bound IDs, assert subscription counts, handle duplicates, and verify missing user behavior.
