# sources/storage-engines/rocksdb/utilities/types_util_test.cc

Purpose: This test file validates `ParseEntry` from `types_util.cc`, with and without user-defined timestamps. It ensures that RocksDB internal-key parsing produces the public `ParsedEntryInfo` shape expected by utility callers.

Important APIs and types: Helpers `EncodeAsUint64` and `IKey` construct expected timestamp encodings and internal keys. The tests use `BytewiseComparator`, `BytewiseComparatorWithU64Ts`, `PutFixed64`, `PackSequenceAndType`, `ValueType::kTypeValue`, `ValueType::kTypeDeletion`, `ParsedEntryInfo`, `EntryType::kEntryPut`, `EntryType::kEntryDelete`, and `ParseEntry`.

Control flow: `InvalidInternalKey` passes an undersized key and a null comparator case, expecting `InvalidArgument`. `Basic` builds normal internal keys for `"foo"` put at sequence 3 and `"bar"` deletion at sequence 5, parses them with the bytewise comparator, and checks empty timestamp, sequence, key, and entry type. `UserKeyIncludesTimestamp` appends fixed64 timestamps to user keys before the internal trailer, parses with the uint64 timestamp comparator, and checks that the returned user key is stripped while timestamp contains the encoded fixed64 bytes.

State and persistence behavior: The tests are pure in-memory construction and parsing. The important lifetime behavior is that expected slices are checked while the backing `std::string ikey` remains alive.

Dependencies and integration points: The suite links the public utility header with internal `dbformat` helpers and RocksDB's timestamp-aware comparator. It is a narrow compatibility guard for utilities that parse internal entries from iterators or diagnostics.

Risks: Coverage is intentionally small: it covers put/delete only, one timestamp comparator, and parse errors for short keys and null comparator. It does not exercise `GetInternalKeyForSeek`, `GetInternalKeyForSeekForPrev`, malformed timestamp lengths, merge/range-delete/value-entity internal types, or caller misuse of output lifetimes.

Test signals: The main signals are exact `Status::InvalidArgument` for invalid inputs and exact parsed `user_key`, `timestamp`, `sequence`, and public `EntryType` for timestamped and non-timestamped entries.
