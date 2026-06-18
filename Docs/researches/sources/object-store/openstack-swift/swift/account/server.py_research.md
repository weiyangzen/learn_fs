# sources/object-store/openstack-swift/swift/account/server.py

Purpose: implements the Swift account-server WSGI controller. It exposes account database operations over internal storage-node HTTP: account create/delete/update/listing, container update fan-in, and account replication RPC dispatch.

Important APIs: `get_account_name_and_placement()` and `get_container_name_and_placement()` validate storage-node paths and internal account/container names. `AccountController` derives from `BaseStorageServer`; `_get_account_broker()` maps account names to hashed account DB paths under `devices/<drive>/accounts/...`; `_deleted_response()`, `check_free_space()`, `_update_metadata()`, and public `DELETE`, `PUT`, `HEAD`, `GET`, `REPLICATE`, `POST` implement the request surface. `app_factory()` and `main()` wire paste.deploy and `run_wsgi`.

Control flow: `__call__()` builds a `Request`, rejects invalid UTF-8 and non-public methods, dispatches to the method named by `req.method`, translates raised `HTTPException` or unexpected exceptions, and logs a Swift request line. `PUT` has two branches: account creation/metadata update, or container row update from container-server notifications. `GET` and `HEAD` use stale-read brokers with short pending timeouts for fast listing/stat responses. `REPLICATE` parses JSON from `wsgi.input` and delegates to `ReplicatorRpc`.

State and persistence: persistent state lives in account SQLite DBs managed by `AccountBroker`; metadata values are timestamped and validated. Container rows store put/delete timestamps, object counts, bytes used, and storage policy index. Delete is logical database deletion. Free-space and mount checks gate mutating requests and replication.

Dependencies and integration: integrates with Swift constraints, request helpers, listing format negotiation, account backend, DB replicator, storage directory hashing, and swob HTTP responses. It is invoked by storage-node WSGI and by container/account replicators.

Risks: correctness depends on timestamp ordering, internal-name validation, broker pending-file behavior, and consistent policy index propagation. Auto-created internal accounts bypass normal account creation only for the configured prefix. Error paths expose tracebacks in 500 bodies. Missing required container-update headers will surface as server errors rather than friendly validation.

Test signals: exercise every HTTP verb, deleted-account states, mount/free-space failures, metadata validation, container update created-vs-deleted response, JSON replication parse failures, invalid UTF-8, logging behavior, and stale-read fallback paths.
