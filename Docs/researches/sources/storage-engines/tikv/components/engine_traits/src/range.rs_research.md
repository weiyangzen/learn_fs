# sources/storage-engines/tikv/components/engine_traits/src/range.rs

Purpose: Defines a borrowed half-open key range shared across engine APIs.

Important APIs and control flow: `Range<'a>` stores `start_key` and `end_key` byte slices. `Range::new` constructs a range without validation.

State, persistence, and dependencies: The type is transient borrowed request state and persists nothing.

Integration points, risks, and test signals: Used by range deletes, ingestion, table/range property queries, memtable stats, and delete strategies. Risks include callers passing reversed bounds, ambiguous empty end-key semantics in different APIs, and lifetime misuse by implementors. Scenario tests cover delete-range inclusive/exclusive, equal bounds, and reversed-range error behavior.
