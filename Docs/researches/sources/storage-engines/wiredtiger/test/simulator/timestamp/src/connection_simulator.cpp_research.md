# sources/storage-engines/wiredtiger/test/simulator/timestamp/src/connection_simulator.cpp

Purpose: implements the connection-level timestamp simulator singleton, global timestamp state, session ownership, and connection `set_timestamp`/`query_timestamp` semantics.

Important APIs and control flow: `get_connection()` returns a static singleton. `open_session()` allocates a new `session_simulator` and stores it in `_session_list`; `close_session()` finds, erases, and deletes it. `query_timestamp()` parses `get=...`, supports `all_durable`, `oldest`, and `stable`, returns success-but-unsupported for several WiredTiger query types, and computes `all_durable` by considering global durable timestamp plus active session commit/durable timestamps. `set_timestamp()` parses `oldest_timestamp`, `stable_timestamp`, `durable_timestamp`, and `force`, validates through `timestamp_manager`, then updates global fields.

State and persistence behavior: process-local singleton state includes `_session_list`, `_oldest_ts`, `_stable_ts`, and `_durable_ts`. There is no durable storage; destructor deletes remaining sessions.

Dependencies and integration points: depends on `session_simulator`, `timestamp_manager`, `error_simulator` macros, STL maps/vectors, and simulator frontends.

Risks: raw owning pointers require correct close/destructor paths. `all_durable` decrements a durable timestamp before comparison, so zero values must be avoided. The simulator intentionally supports only a subset of WiredTiger timestamp query/config options.

Test signals: call-log replay and CLI queries should match expected hex timestamps and validation failures for supported connection-level operations.
