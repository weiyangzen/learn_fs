# sources/storage-engines/foundationdb/fdbserver/UID.swift

## Purpose
`UID.swift` adds Swift collection compatibility for the C++/Flow `UID` type exposed through `FDBServer`. It makes `Flow.UID` conform to `Hashable` so it can be used as a dictionary key, set element, or any other Swift hash-based identity.

## Important APIs, Types, and Functions
The only public API is an extension on `Flow.UID`. `hash(into:)` feeds `first()` and `second()` into the Swift hasher. `==` returns true only when both 64-bit halves match.

## Control Flow
There is no asynchronous or branching control flow beyond the equality comparison. Hashing and equality use the same two components, which preserves Swift's requirement that equal values hash identically.

## State and Persistence Behavior
The extension stores no state and performs no persistence. It depends on `UID.first()` and `UID.second()` being stable views of the underlying UID value.

## Dependencies and Integration Points
The file imports `Flow` and `FDBServer`, then extends the Flow type from Swift. The integration point is Swift code that needs FoundationDB identifiers in standard-library hashed collections.

## Risks and Test Signals
The risk is semantic drift if the underlying UID representation changes or if `first()`/`second()` no longer represent the full identity. Unit coverage should include two identical UIDs comparing equal and hashing consistently, plus different first or second halves comparing unequal.
