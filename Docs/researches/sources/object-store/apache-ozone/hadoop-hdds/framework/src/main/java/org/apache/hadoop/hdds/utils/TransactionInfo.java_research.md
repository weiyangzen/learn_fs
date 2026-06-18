# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/TransactionInfo.java

## Purpose
`TransactionInfo` is an immutable persisted representation of a Ratis term and transaction index. It is stored in Ozone metadata DBs and can also be exposed as Ratis `SnapshotInfo`.

## Important APIs and Types
Static constructors include `valueOf(String)`, `valueOf(long, long)`, `valueOf(TermIndex)`, and non-Ratis `getTermIndex(long)`. `getCodec` returns a `DelegatedCodec` over `StringCodec`. Accessors include `getTerm`, `getTransactionIndex`, `getTermIndex`, `toByteString`, `fromByteString`, `toSnapshotInfo`, and `readTransactionInfo(DBStoreHAManager)`.

## Control Flow and State
The persisted string is `term + TRANSACTION_INFO_SPLIT_KEY + index`. Parsing validates exactly two fields and converts both to longs. The constructor creates an anonymous `SnapshotInfo` whose term-index and `toString` mirror the immutable transaction string; `getFiles` returns null.

## Persistence, Dependencies, and Integration
This is directly persisted under `TRANSACTION_INFO_KEY` in HA metadata tables and read by HA checkpoint validation. Dependencies include Guava preconditions, Protobuf `ByteString`, HDDS codecs, Ratis `TermIndex`, `SnapshotInfo`, and DB HA manager interfaces.

## Risks and Test Signals
Malformed transaction strings throw `IllegalArgumentException`. The anonymous `SnapshotInfo.getFiles` returning null may surprise generic snapshot code. Ordering delegates to `TermIndex.compareTo`. Tests should cover codec round trips, byte-string conversion, default value semantics, non-Ratis term handling, compare/equality/hash consistency, malformed strings, and DB read skip-cache behavior.
