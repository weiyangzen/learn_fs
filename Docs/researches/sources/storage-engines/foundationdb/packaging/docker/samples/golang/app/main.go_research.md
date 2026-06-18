# sources/storage-engines/foundationdb/packaging/docker/samples/golang/app/main.go

Purpose: This Go sample exposes a minimal HTTP counter backed by FoundationDB. It demonstrates opening FDB from container environment and performing a transactional read-modify-write.

Important APIs and functions: `main` parses `FDB_API_VERSION`, calls `fdb.MustAPIVersion`, opens the database from `FDB_CLUSTER_FILE`, registers `/counter`, and starts `http.ListenAndServe`. `incrementCounter` runs `db.Transact`, reads key `my-counter`, increments a big-endian uint32, writes it back, and returns the new value.

Control flow: Each request to `/counter` performs one FDB transaction. Missing values initialize to zero before incrementing. Errors from the transaction call `log.Fatalf`, terminating the server.

State and persistence behavior: Persistent state is a single FDB key `my-counter` encoded as 4-byte big-endian unsigned integer. The global `db` holds the database connection.

Dependencies and integration points: It uses the FoundationDB Go binding, Go `net/http`, environment variables from Docker Compose, and helper functions for binary conversion.

Risks: The counter overflows at `uint32` limits and fatal request errors kill the whole process. Only GET-like `/counter` increments; there is no read-only route. Tests should cover first increment, concurrent increments, transaction retry behavior, bad env parsing, and overflow if relevant.
