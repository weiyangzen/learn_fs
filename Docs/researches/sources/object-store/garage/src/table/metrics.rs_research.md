# sources/object-store/garage/src/table/metrics.rs

Purpose: OpenTelemetry metrics for per-table storage size, queues, operations, and sync traffic.

Important APIs and types: `TableMetrics` owns value observers for table size, Merkle tree size, Merkle todo length, insert queue length, and GC todo length; bound counters/recorders for get and put requests; counters for internal updates/deletes; and counters for sync items sent/received. `TableMetrics::new` binds instruments to a table name.

Control flow: observers call `approximate_len` on the relevant DB trees when scraped. Request/update/delete counters are incremented by table operations elsewhere. Sync counters are recorded by `sync.rs`.

State and persistence: no persistent state in the metrics object. It keeps cloned DB tree handles so observers can query live approximate lengths.

Dependencies and integration: constructed by `TableData::new`, used in data mutation, table API, sync sending/receiving, and background status.

Risks and test signals: observer closures must not panic if DB length calls fail; the code ignores errors. The GC observer block shows indentation drift, but behavior is simple. Bound table-name labels keep per-table metrics stable; sync counters add `to`/`from` labels with node IDs. No direct tests.
