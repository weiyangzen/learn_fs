# sources/storage-engines/foundationdb/layers/pubsub/ps_prompt.py

Purpose: This is an interactive prompt bootstrap for manually experimenting with the pub/sub layer against a remote FoundationDB database. It imports bindings, opens a named database, and creates a `PubSub` instance.

Important APIs and types: It imports `fdb` and `PubSub` from `pubsub_bigdoc`, then exposes `db` and `ps` in an interactive Python session due to the `#!/usr/bin/python -i` shebang.

Control flow: On execution it prepends a local bindings path, opens `10.0.3.1:2181/bbc` database `TwitDB`, and constructs `ps = PubSub(db)`. There are no functions or guards.

State and persistence behavior: The script does not mutate state directly, but the exposed `ps` object can mutate the configured remote database from the prompt. The hard-coded connection string is persistent operational configuration embedded in source.

Dependencies and integration points: It depends on a `pubsub_bigdoc` module not included in this listed subset and on legacy multi-argument `fdb.open` semantics. It is a developer convenience wrapper, not a reusable library.

Risks: Running it in the wrong environment points at a hard-coded remote database. Tests are not appropriate beyond smoke-checking import/open against a test cluster; safer usage would parameterize the cluster/database and avoid import-time connection side effects.
