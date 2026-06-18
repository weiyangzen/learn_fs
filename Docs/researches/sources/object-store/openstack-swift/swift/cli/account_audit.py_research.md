# sources/object-store/openstack-swift/swift/cli/account_audit.py

Purpose: operational consistency auditor for accounts, containers, and objects. It walks Swift rings, talks directly to storage nodes, compares listings/counts/ETags across replicas, and optionally downloads objects to verify checksums.

Important APIs: `Auditor.__init__()` loads account, container, and object rings and initializes counters, caches, and in-progress events. `audit_account()`, `audit_container()`, and `audit_object()` perform replica-level checks. `audit()` chooses depth from a parsed path; `wait()` joins green threads; `print_stats()` summarizes mismatches. `main()` parses `-c`, `-r`, `-e`, `-d`, arguments, and stdin paths.

Control flow: account audit gets all account replicas, pages JSON listings by marker, compares account container/object counts, caches container names, and optionally recurses into containers. Container audit first verifies account listing membership, then pages every container replica, compares object versions and object counts, caches object listings, and optionally spawns object audits. Object audit verifies container listing membership, HEADs or GETs each object replica, checks ETags and optional MD5, and writes inconsistent paths to the error file.

State and persistence: mostly read-only network probing. Persistent output is optional append-only error-file entries. In-memory `list_cache` and `in_progress` events avoid duplicate concurrent listing fetches.

Dependencies and integration: uses Swift `Ring`, `http_connect`, `split_path`, eventlet `GreenPool`/`Event`, direct storage-node endpoints, and MD5 helpers.

Risks: can generate heavy direct-node load, especially with deep download mode. It assumes JSON listing format and specific replica headers. A small bug prints an account error path with `print(path, error_file)` instead of `file=error_file`. Unicode path encoding differs by account/container/object segment.

Test signals: mock rings and HTTP responses for replica divergence, marker paging, cache synchronization, deep checksum mismatch, error-file writes, stdin path parsing, and counter summaries.
