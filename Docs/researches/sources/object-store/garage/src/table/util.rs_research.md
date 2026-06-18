<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/table/util.rs -->
# sources/object-store/garage/src/table/util.rs

## Purpose
Small table helper types shared by schemas and range reads. It supplies an empty partition/sort key, deletion filtering policy, and range enumeration direction.

## Important APIs, types, and functions
`EmptyKey` implements both `SortKey` and `PartitionKey`, returning an empty byte sort key and a zero hash. `DeletedFilter` has `Present`, `Deleted`, and `Any` variants with `apply`. `EnumerationOrder` has `Forward`, `Reverse`, and `from_reverse`.

## Control flow
The helpers are pure value conversions. Table data/range code applies `DeletedFilter` to per-entry deleted state and `EnumerationOrder` to choose forward or reverse traversal/trimming.

## State and persistence behavior
No persistent state is stored here. The enum values are serializable and become part of table RPC/range request state when clients enumerate metadata.

## Dependencies and integration points
Depends on table `PartitionKey`/`SortKey` traits and `garage_util::data::Hash`. `EmptyKey` is used for singleton/global table partitions such as bucket aliases.

## Risks and test signals
The zero hash for `EmptyKey` intentionally maps all singleton rows to one partition; accidental use for high-cardinality data would hot-spot a shard. Tests should cover filter truth tables and reverse flag conversion.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/table/util.rs -->
