# sources/object-store/garage/fuzz/src/lib.rs

Purpose: provides a generic fuzz/test helper for validating CRDT merge laws used by Garage table state.

Important API: `check_crdt_laws<T>(a, b, c)` accepts any `T: Crdt + PartialEq + Clone + Debug` and asserts idempotency, commutativity, a corollary idempotency after merge, and associativity.

Control flow and state: the helper clones inputs, mutates the clones through `merge`, and compares resulting values with `assert_eq!`. It has no persistence and no external side effects beyond panics on law violations.

Dependencies/integration: depends on `garage_table::crdt::Crdt` and Rust `Debug`. Fuzz targets can instantiate arbitrary CRDT values and call this helper to catch merge implementations that would make distributed table reconciliation non-convergent.

Risks: it validates algebraic laws for three provided values only; fuzz quality depends on generators. It does not test serialization, tombstone compaction, timestamp monotonicity, or partial-order semantics unless encoded in generated values.

Test signals: useful failures are assertion messages showing non-idempotent, non-commutative, or non-associative merges. Add fuzz corpora for CRDT values with deletes, concurrent updates, equal timestamps, and empty/default states.
