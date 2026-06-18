# sources/storage-engines/foundationdb/layers/pubsub/remoteload.py

Purpose: This command-line utility bulk-creates paired users for a remote pub/sub benchmark: each user gets both an inbox and a feed. It is meant to seed a remote FoundationDB database before subscription/message workloads.

Important APIs and functions: It parses `--zkAddr`, `--database`, `--userStart`, and `--userCount`, opens `fdb.open(args.zkAddr, args.database)`, constructs `PubSub`, and calls `create_inbox_and_feed` with zero-padded user names.

Control flow: The script loops from `userStart` to `userCount - 1`, creates each user, prints progress every 100 users, then prints done. A transactional done-marker block is present but commented out.

State and persistence behavior: Persistent state is whatever `pubsub_bigdoc.PubSub.create_inbox_and_feed` writes for each user. There is no rollback across the whole range; partial loads remain if the script fails.

Dependencies and integration points: It uses argparse, legacy local bindings path insertion, and `pubsub_bigdoc`. It is one component of the remote pub/sub benchmark trio with `remotesubscribe.py` and `remotesend.py`.

Risks: Argument names reflect old ZooKeeper-style cluster addressing. Range semantics may surprise users because `userCount` is an exclusive end, not a count from start. Tests should run against an isolated database and assert created feed/inbox counts and idempotence for repeated ranges.
