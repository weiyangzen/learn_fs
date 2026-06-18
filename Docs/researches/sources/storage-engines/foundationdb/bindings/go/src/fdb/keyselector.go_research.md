<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/keyselector.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/keyselector.go

Purpose: defines Go representations of FoundationDB key selectors.

Important APIs: `Selectable`, `KeySelector`, `FDBKeySelector`, and constructors `LastLessThan`, `LastLessOrEqual`, `FirstGreaterThan`, `FirstGreaterOrEqual`.

Control flow: constructors fill the selector triple `(key, orEqual, offset)` using FoundationDB's standard selector formulas. Transactions later convert these fields into C `fdb_transaction_get_key` and range selector arguments.

State and persistence: no state or persistence. Selectors are immutable value descriptions.

Dependencies and integration: depends on `KeyConvertible`. Used by `Range`, `SelectorRange`, tuple/subspace range selector implementations, and transaction get/range APIs.

Risks: off-by-one semantics are subtle; constructor field values must exactly match FoundationDB selector definitions. Passing nil `KeyConvertible` would panic later when converting. Selector resolution can read database state and conflict depending on transaction options.

Test signals: range examples and iterator tests indirectly exercise `FirstGreaterOrEqual` and `FirstGreaterThan`; direct selector resolution tests would strengthen coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/keyselector.go -->
