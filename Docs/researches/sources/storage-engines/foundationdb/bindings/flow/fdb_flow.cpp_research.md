## sources/storage-engines/foundationdb/bindings/flow/fdb_flow.cpp

Purpose: implements Flow-style asynchronous wrappers around the FoundationDB C API, exposing `API`, `DatabaseImpl`, and `TransactionImpl`.

Important APIs and functions: `CFuture::blockUntilReady`, `backToFutureCallback`, and templated `backToFuture` bridge raw `FDBFuture*` callbacks onto the Flow network thread and convert results. `API` implements version selection, network options/setup/run/stop, database creation, predicate evaluation, and API version access. `DatabaseImpl` wraps database options and admin calls. `TransactionImpl` wraps reads, ranges, split points, conflicts, mutations, commit, versionstamp, size, onError, cancel, and reset.

Control flow: each C API future is wrapped in `Reference<CFuture>`, callback completion schedules a Flow promise on `g_network`, and conversion reads the future result after awaiting readiness. Returned `FDBStandalone<T>` values hold the `CFuture` reference so borrowed C result memory remains valid.

State and persistence: owns raw `FDBDatabase*` and `FDBTransaction*` lifetimes. Mutations persist through `commit`; read result memory persists through future ownership.

Dependencies and integration points: depends on C API, Flow actors/network, `FDBLoanerTypes`, deterministic random/test helpers in the local `fdb_flow_test`, and admin C API functions.

Risks: `backToFuture` assumes callback registration succeeds and that `g_network` is available. Range result casts C structs to Flow `KeyValueRef`/`KeyRef` layout-compatible types. API singleton is process-global and enforces one selected API version.

Test signals: unit tests and directory tester rely on these wrappers for all Flow binding database operations.
