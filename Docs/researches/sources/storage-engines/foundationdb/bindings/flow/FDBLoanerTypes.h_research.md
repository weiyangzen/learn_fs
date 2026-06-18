## sources/storage-engines/foundationdb/bindings/flow/FDBLoanerTypes.h

Purpose: supplies Flow-binding stand-ins for common FoundationDB client types: keys, values, key selectors, key-value pairs, range results, range limits, key ranges, and debug describe helpers.

Important APIs and types: defines `KeyRef`, `ValueRef`, `Version`, `Key`, `Value`, `KeySelectorRef`, `KeySelector`, `KeyValueRef`, `RangeResultRef`, `GetRangeLimits`, and `KeyRangeRef`. Helpers implement `keyAfter`, key selector constructors, range pagination helpers, range intersection, limit accounting declarations, and container `describe` functions.

Control flow: range reads return `RangeResultRef`, whose `more`, `readThrough`, `nextBeginKeySelector`, and `nextEndKeySelector` guide pagination. `KeyRangeRef` validates begin <= end and throws `inverted_range`.

State and persistence: no database writes; these types carry arena-backed views and standalones used by wrapper futures and directory logic.

Dependencies and integration points: used throughout `fdb_flow.*`, `Subspace`, `DirectoryLayer`, `Tuple`, and tests. `FDBStandalone` in `fdb_flow.h` often wraps these types to keep raw C future memory alive.

Risks: many types are borrowed `StringRef`/`VectorRef` views, so lifetime and arena ownership are critical. `keyAfter("\xff\xff")` special-cases the maximum system key boundary.

Test signals: range and directory tests validate key selector/range behavior indirectly.
