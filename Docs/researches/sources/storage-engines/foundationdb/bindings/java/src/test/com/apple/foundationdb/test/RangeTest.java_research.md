# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/RangeTest.java

Purpose: manual integration smoke test for basic range reads, cancellation behavior, clear ranges, and `Range.equals/hashCode`.

Important APIs and flow: `main` writes `apple1` through `apple6`, calls `checkRange`, verifies canceled transactions return FDB error 1025 on a subsequent get, clears `apple3` through `apple6`, checks the range again, and compares several `Range` instances including null endpoints. `checkRange` reads a value, obtains a limited selector range as a list, then iterates the same `AsyncIterable`.

State and persistence: writes and clears user-space `apple*` keys. Dependencies include `FDB`, `Database.run`, `Transaction`, `KeySelector`, `Range`, and `AsyncIterable`. Risks include non-isolated test keys, stdout-based validation for range contents, and direct assumptions about cancellation error codes. Signal is exceptions for hard failures and printed diagnostics for range equality.
