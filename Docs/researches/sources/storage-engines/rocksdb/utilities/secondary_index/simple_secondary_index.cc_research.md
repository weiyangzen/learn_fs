# sources/storage-engines/rocksdb/utilities/secondary_index/simple_secondary_index.cc

Purpose: implements a simple secondary index whose secondary key prefix is the indexed primary column value encoded as a length-prefixed slice.

Important APIs and control flow: constructor stores the primary column name. Setters/getters bind primary and secondary column families. `UpdatePrimaryColumnValue()` leaves the primary value unchanged. `GetSecondaryKeyPrefix()` returns the primary column value, `FinalizeSecondaryKeyPrefix()` encodes it with `PutLengthPrefixedSlice`, and `GetSecondaryValue()` leaves the secondary value empty.

State and persistence: state is only the configured column handles and column name; persisted secondary data is maintained by `SecondaryIndexMixin` in the secondary column family as finalized prefix plus primary key.

Dependencies and integration: uses public `secondary_index_simple.h`, varint/length-prefixed coding, and `SecondaryIndexHelper`.

Risks and test signals: the implementation assumes secondary key ordering over length-prefixed values is acceptable for equality/prefix scans, not arbitrary value-range ordering. Empty secondary values mean all payload must come from primary lookup or key suffix. Coverage is likely through broader secondary-index tests outside this file set.
