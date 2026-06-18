# sources/object-store/openstack-swift/swift/cli/info.py

Purpose: shared implementation for `swift-account-info`, `swift-container-info`, `swift-object-info`, and `swift-get-nodes` style introspection. It reads DBs/datafiles, prints metadata and sync/sharding state, and computes ring placement plus direct curl/ssh hints.

Important APIs: `InfoSystemExit`, `parse_get_node_args()`, `curl_head_command()`, `print_ring_locations()`, `print_db_info_metadata()`, `print_obj_metadata()`, `print_info()`, `print_obj()`, `print_item_locations()`, and entry points `obj_main()`, `container_main()`, `account_main()`.

Control flow: DB info opens an `AccountBroker` or `ContainerBroker`, reads broker info and metadata, adds deletion and shard-range details, prints metadata grouped by user/system prefixes, optionally prints sync tables, then attempts ring placement. Object info reads diskfile metadata, prints object metadata including crypto details, optionally streams the file to verify ETag/content length, extracts policy from path, and prints ring locations. `print_item_locations()` selects account/container/object ring behavior from supplied path, ring, policy, or partition.

State and persistence: read-only, except it may trigger broker pending commit behavior indirectly through broker reads depending on backend behavior. It reads SQLite DBs, object datafiles, rings, and swift config.

Dependencies and integration: uses account/container brokers, diskfile metadata, storage policies, ring hashing, metadata prefix helpers, crypto metadata decoding, SQLite, and lock-timeout fallback.

Risks: object ETag checking reads whole datafiles and can be expensive. `print_obj_metadata()` mutates its metadata dict with `pop()`. Stale DB reads are retried after `OperationalError` or `LockTimeout`, exiting with code 2. Incorrect policy/ring combinations print warnings but still produce output.

Test signals: cover DB type validation, stale-read fallback, shard-range summary/verbose output, sync-table output, object crypto metadata, ETag mismatch, IPv6 curl formatting, policy extraction, quoted get-node args, and all entry-point exit paths.
