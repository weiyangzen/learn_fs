# sources/storage-engines/foundationdb/bindings/python/tests/unit_tests.py

Purpose: This file orchestrates Python binding unit tests against a live FoundationDB cluster.

Important APIs and types: It imports cancellation/timeout tests, size-limit tests, `fdb.transactional`, database and transaction option methods, watches, locality helpers, predicates, and client status retrieval. `run_unit_tests(db)` is the main entry point.

Control flow: Standalone mode selects latest API version, parses a cluster file, opens the database, and runs `run_unit_tests`. The test sequence covers database options, transaction options, watches, cancellation, retry limits, timeouts, locality, predicates, size limits, approximate transaction size, and client status JSON. It also checks generator rejection behavior for `@transactional` at API version 630+.

State and persistence behavior: Tests write and mutate keys such as `w0` through `w3`, use watches, set database-level defaults, and read system keys for locality. Some tests sleep and retry until watch/locality behavior is stable.

Dependencies and integration points: It integrates most Python binding modules and is also invoked by `tester.py` through the `UNIT_TESTS` instruction. Client status parsing depends on JSON returned by the C API.

Risks: Requires a live cluster and may be timing-sensitive for watches and locality. Options and timeout defaults must be reset by subtests. Generator behavior assertions depend on selected API version.

Test signals: Successful full sequence, exact option invocation coverage, watch readiness transitions, locality consistency, predicate truth values, client status with `Healthy: true`, and propagated failure descriptions.
