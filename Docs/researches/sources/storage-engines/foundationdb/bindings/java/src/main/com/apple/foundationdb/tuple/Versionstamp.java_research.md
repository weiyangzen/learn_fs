<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/Versionstamp.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/Versionstamp.java

## Purpose
`Versionstamp` represents the 12-byte FoundationDB versionstamp tuple value: 10 transaction-version bytes plus a 2-byte user version.

## Important APIs, Types, And Functions
Static APIs are `fromBytes`, `incomplete`, `incomplete(int)`, `complete(byte[])`, `complete(byte[], int)`, and `unpackUserVersion`. Instance APIs include `isComplete`, `getBytes`, `getTransactionVersion`, `getUserVersion`, `compareTo`, `equals`, `hashCode`, and `toString`.

## Control Flow
Factories validate lengths and unsigned-short user version bounds, then create big-endian 12-byte arrays. `fromBytes` marks a stamp complete if any transaction-version byte differs from the all-`0xff` incomplete sentinel. Comparison sorts complete stamps before incomplete stamps; complete stamps compare unsigned by all bytes, incomplete stamps compare by user version.

## State And Persistence Behavior
State is `complete` plus `versionBytes`. `getBytes` deliberately returns the internal array for performance, so callers can mutate the object if careless. Incomplete stamps are used with `SET_VERSIONSTAMPED_KEY` and completed by the database at commit time.

## Dependencies And Integration Points
`TupleUtil` encodes/decodes versionstamps and enforces incomplete versionstamp count. `Tuple` and `Subspace` expose versionstamp packing. `VersionstampSmokeTest` and tuple tests exercise database round trips.

## Risks And Test Signals
Risks include internal byte-array mutation, sentinel completeness detection, unsigned user-version bounds, compare order for complete versus incomplete stamps, and interaction with tuple versionstamp offsets. Tests should cover factory validation, equality/hash after mutation risks, user-version unpacking, tuple pack/unpack, and actual database versionstamped mutations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/Versionstamp.java -->
