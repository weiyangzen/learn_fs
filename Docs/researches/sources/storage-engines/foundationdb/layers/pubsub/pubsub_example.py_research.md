# sources/storage-engines/foundationdb/layers/pubsub/pubsub_example.py

Purpose: This standalone example drives `pubsub.PubSub` with a randomized threaded topology. It is a demonstration of feeds posting messages and inboxes polling for received messages.

Important APIs and functions: It creates a module-level `ps = PubSub(db)` and defines `setup_topology`, `feed_driver`, `get_and_print_inbox_messages`, `inbox_driver`, `run_threads`, and `sample_pubsub`.

Control flow: The script clears all pub/sub state, creates a requested number of feeds and inboxes, randomly subscribes each inbox to at least one feed, starts one thread per feed to post messages with random sleeps, and starts one thread per inbox to poll until no changes are observed for a wait limit.

State and persistence behavior: It mutates the default FDB database through the PubSub layer and clears all messages at startup. Runtime state is Python thread lists and polling variables; persistent state is the SimpleDoc-backed pub/sub tree.

Dependencies and integration points: It uses `fdb.api_version(22)`, Python `random`, `threading`, and `time`, and the local `pubsub` module. It listens to no external input other than the hard-coded sample sizes in `__main__`.

Risks: Output is nondeterministic due to random topology and sleep timing. It is Python 2 syntax and not an automated test. Test signals are visual logs; a real test should assert expected message counts and subscription coverage with deterministic random seeds.
