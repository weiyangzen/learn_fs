# sources/storage-engines/rocksdb/utilities/types_util.cc

Purpose: This file implements small utility functions that bridge public utility code and RocksDB internal-key encoding. It constructs synthetic internal keys suitable for forward and reverse seeks, and parses internal keys back into public `ParsedEntryInfo` fields including optional user-defined timestamps.

Important APIs and types: The exported functions are `GetInternalKeyForSeek`, `GetInternalKeyForSeekForPrev`, and `ParseEntry`. They use `Comparator::timestamp_size`, `Comparator::GetMaxTimestamp`, `Comparator::GetMinTimestamp`, `PutFixed64`, `PackSequenceAndType`, `kMaxSequenceNumber`, `kValueTypeForSeek`, `kValueTypeForSeekForPrev`, `ParseInternalKey`, `ParsedInternalKey`, `StripTimestampFromUserKey`, `ExtractTimestampFromUserKey`, and `GetEntryType`.

Control flow: The seek-key helpers first reject a null comparator, derive the comparator's timestamp size, fetch the comparator's maximum or minimum timestamp, and reject inconsistent timestamp lengths. They then overwrite the caller-provided buffer with the user key, append max timestamp for forward seek or min timestamp for reverse seek when timestamps are enabled, and append the packed internal trailer. `ParseEntry` rejects undersized internal keys and null comparators, delegates trailer parsing to `ParseInternalKey`, validates that the parsed user-key-with-timestamp is large enough for the comparator's timestamp size, strips and extracts timestamp slices when needed, and fills user key, timestamp, sequence, and public entry type.

State and persistence behavior: The functions are stateless and do not persist anything. The caller-owned `std::string` buffer receives owned internal-key bytes. `ParsedEntryInfo` receives `Slice` fields that reference the input internal key; callers must keep the input alive for as long as they inspect those slices.

Dependencies and integration points: The implementation depends on `db/dbformat.h`, so it is utility-facing code with direct knowledge of RocksDB's internal key trailer. It is used by utilities that need to seek or inspect internal entries while respecting user-defined timestamp comparators.

Risks: Comparator timestamp contracts are critical. If `GetMaxTimestamp` or `GetMinTimestamp` returns the wrong length, the helper fails early; if the comparator lies consistently, internal seek behavior can be wrong. `ParseEntry` does not null-check `parsed_entry`, so callers must pass a valid output pointer. Timestamp stripping assumes the comparator's timestamp size matches the key encoding. The helpers construct keys for seek ordering, not for user-visible persistence.

Test signals: The paired tests cover invalid internal-key length, null comparator rejection, parsing of put and delete entries without timestamps, and parsing of put and delete entries with the built-in uint64 timestamp comparator. The seek-key construction helpers are not directly covered in the listed test file.
