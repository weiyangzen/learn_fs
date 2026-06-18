# sources/storage-engines/rocksdb/db/output_validator.cc

## Purpose
`output_validator.cc` implements `OutputValidator::Add`, a compact validator used while building SST output. It checks internal-key structural validity, enforces nondecreasing internal-key order, and optionally maintains a rolling paranoid hash over emitted keys and values.

## Important APIs, Types, And Functions
The single function is `Status OutputValidator::Add(const Slice& key, const Slice& value)`. It uses `NPHash64` for rolling key/value hashing when hashing is enabled, `kNumInternalBytes` to reject keys too short to contain an internal suffix, and `InternalKeyComparator::Compare` to detect out-of-order output.

## Control Flow
`Add` first updates `paranoid_hash_` with the key and then the value if `enable_hash_` is true. It then rejects any key shorter than RocksDB's internal key trailer. If a previous key exists and the new key compares less than it, the function returns corruption. Otherwise it copies the current key into `prev_key_` and returns OK.

## State And Persistence Behavior
The validator keeps only transient state: previous internal key and rolling hash. It does not persist the hash and the header explicitly says the hash is not a stable cross-release format. Its purpose is runtime validation and comparison between produced and read-back output sequences.

## Dependencies And Integration Points
The file depends on `db/output_validator.h`, `util/hash.h`, and `InternalKeyComparator`. It is integrated with compaction/table-building paths that feed every output key/value through a validator and may compare validators after reading output back.

## Risks
Ordering is only as correct as the supplied internal comparator. The check permits equal keys because it only rejects `Compare < 0`; this matches the broad invariant of nondecreasing order but relies on upstream compaction rules for duplicate internal-key constraints.

Hashing includes raw key and value bytes in sequence. Any caller expecting a persisted or portable checksum would be wrong; `GetHash` is intentionally unstable between releases.

## Test Signals
Expected signals are corruption statuses for keys shorter than `kNumInternalBytes` and for out-of-order internal keys, stable matching hashes for identical key/value streams, and OK status for correctly ordered SST output.
