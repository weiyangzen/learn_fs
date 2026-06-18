# sources/storage-engines/foundationdb/packaging/docker/samples/python/app/server.py

Purpose: This Flask sample exposes read and increment endpoints for a FoundationDB-backed counter. It demonstrates Python binding setup and transactional mutation from a web service.

Important APIs and functions: It sets `fdb.api_version(int(os.getenv("FDB_API_VERSION")))`, opens the default database, defines `COUNTER_KEY = fdb.tuple.pack(("counter",))`, implements `_increment_counter(tr)`, and exposes `GET /counter` plus `POST /counter/increment`.

Control flow: `GET /counter` reads the key directly and returns `0` when absent. `POST /counter/increment` calls `_increment_counter(db)`, relying on the binding's transactional decorator behavior for functions accepting a transaction-like first argument.

State and persistence behavior: Persistent state is one tuple-packed counter key storing a tuple-packed integer. The Flask process holds a global database object.

Dependencies and integration points: It uses Flask and the FoundationDB Python binding. The start script prepares cluster connectivity and starts `flask run`.

Risks: The increment helper lacks an explicit `@fdb.transactional` decorator in this file, so correctness depends on binding behavior when passing `db` to an undecorated function; in standard bindings this would not make `tr[COUNTER_KEY]` valid unless `db` supports direct reads. Tests should verify POST actually commits, concurrent increments are atomic, and missing/invalid `FDB_API_VERSION` fails clearly.
