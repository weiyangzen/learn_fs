# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/KeyBackedTypes.h

## Purpose
Defines typed wrappers for storing scalar values, maps, sets, watch triggers, and related records in FoundationDB keyspaces. The core goal is to let system metadata code use strongly typed keys and values while preserving FDB tuple/binary/object encoding and transaction semantics.

## Important APIs, Types, And Functions
`TupleCodec` and specializations pack/unpack ints, bools, strings, UIDs, versionstamps, pairs, vectors, key ranges, and enums. `NullCodec`, `BinaryCodec`, and `ObjectCodec` provide alternate value encodings. `KeyBackedRangeResult` standardizes paged results. `WatchableTrigger` updates a versionstamped key, reads it, watches it, and exposes `onChange()` loops. `KeyBackedProperty` stores one typed value at one key with optional trigger updates and transaction-creator overloads that set system-key and lock-aware options. `KeyBackedBinaryValue` adds atomic and versionstamp operations. `TypedKeySelector` converts typed selectors to FDB key selectors. `KeyBackedMap` and `KeyBackedSet` expose typed get/range/seek/set/erase/clear/conflict-range operations under a prefix. `KeyBackedClass` packages a `Subspace` plus default change trigger.

## Control Flow
Transaction-creator overloads use `runTransaction()` to create transactions and set required options before recursively calling transaction overloads. Range reads unpack FDB keys/values into typed results and preserve `more`. Selector-based range reads defensively filter raw results to the subspace and continue internally if a page contains only out-of-subspace keys, ensuring callers receive a usable continuation point. Seeks map `<`, `<=`, `>`, and `>=` to bounded one-row range reads. Writes update the optional trigger after each mutation.

## State And Persistence Behavior
All durable state is ordinary FDB key/value data under configured prefixes, encoded by the chosen codec. Sets store empty values; maps store encoded values; properties store one encoded value. Triggers persist versionstamped values whose versions can be watched. The classes themselves are small handles containing prefixes, codecs, and optional triggers.

## Dependencies And Integration Points
The header depends on client boolean params, commit transaction references, run-transaction helpers, generated options, generic transaction helpers, subspaces, tuple versionstamps, object serialization, Flow coroutines, and thread futures. It is a central integration layer for FoundationDB system metadata and management code.

## Risks And Test Signals
Risks include codec incompatibility or schema drift, incorrect system-key access options, trigger updates without intended conflict ranges, selector reads touching unreadable/offline ranges, versionstamp offset mistakes, and borrowed `StringRef` lifetime issues. Test signals should include codec round trips, map/set pagination and reverse reads, seek behavior at boundaries, trigger watch/onChange behavior, transaction creator overloads, conflict range generation, versionstamped value writes, and filtering when selectors resolve outside the subspace.
