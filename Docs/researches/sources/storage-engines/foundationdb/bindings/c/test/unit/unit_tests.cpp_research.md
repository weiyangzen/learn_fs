## sources/storage-engines/foundationdb/bindings/c/test/unit/unit_tests.cpp

Purpose: comprehensive doctest-based regression coverage for the latest FoundationDB C API through the C++ convenience wrapper in `fdb_api.hpp`. The file sets up the FDB network, opens a database from a cluster file, scopes data under a caller-provided `prefix`, and exercises futures, transactions, range reads, mapped range reads, tuple/versionstamp behavior, watches, special key space, admin calls, error predicates, and allocator cleanup.

Important APIs and functions: `fdb_check`, `fdb_open_database`, `wait_future`, `strinc_str`, `insert_data`, `get_value`, `get_range`, and `get_mapped_range` centralize error handling and retry-friendly access. The test cases cover `FDBFuture` getters, callbacks, cancellation, memory release, `FDBTransaction` read/write/range/atomic/watch/conflict APIs, database options, special key space reads/writes, `fdb_database_get_server_protocol`, reboot/recovery/snapshot calls, and `fdb_error_predicate`.

Control flow: most transaction tests use a retry loop around `wait_future`, call `tr.on_error(err)` for retryable failures, and then assert once a successful attempt returns. Setup helpers clear the prefix range before installing test data. The `main` function selects `FDB_API_VERSION`, optionally configures an external client library, starts the network on a thread, runs doctest, destroys the database, and stops the network.

State and persistence: tests mutate real database keys under `prefix`, tuple-encoded record/index keys, system keys with access options, and special keys under `\xff\xff/tracing`. They explicitly reset database options changed during a test, such as transaction size limits and max watches. Watch and conflict tests rely on transaction lifecycle state, commit versions, and retry semantics.

Dependencies and integration points: depends on generated C API options, `foundationdb/fdb_c.h`, doctest, RapidJSON status parsing, Flow random/UID/config utilities, and `fdbclient/Tuple`. It validates the binding contract between the public C API, the wrapper classes, and a live local/test cluster.

Risks: tests assume a reachable single-process cluster for `fdb_database_reboot_worker`; comments note sensitivity to configuration and TSAN. Some assertions are guarded when commit unknown/retry behavior means an atomic operation may have committed multiple times. Hard-coded error codes make this an API compatibility sentinel but can require updates if semantics intentionally change.

Test signals: this file is itself a high-value integration test suite. It signals expected behavior for future memory ownership, callback ordering, read-your-writes options, range pagination flags, mapped-range restrictions, versionstamped mutations, special key space tracing, network thread blocking protection, and thread-local allocation cleanup.
