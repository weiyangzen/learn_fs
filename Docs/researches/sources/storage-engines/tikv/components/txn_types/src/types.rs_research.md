# sources/storage-engines/tikv/components/txn_types/src/types.rs

## Purpose
Defines core transaction-facing data types for TiKV MVCC storage: encoded keys, values, mutations, old-value capture, transaction extra data, write-batch flags, last-change hints, and commit roles. The file is the shared vocabulary between RPC mutation inputs, MVCC storage internals, CDC old-value capture, and Raft request metadata.

## Important APIs, Types, and Functions
`Value`, `ValueEntry`, `KvPair`, and `KvPairEntry` wrap raw byte values with optional commit timestamps. `Key` owns the encoded key representation and exposes raw/encoded conversion, timestamp append/truncate/split/decode helpers, encoded/raw equality helpers, hash generation, formatting, cloning with timestamp reserve capacity, and heap sizing. `Mutation` maps `kvrpcpb::Mutation` into internal variants (`Put`, `Delete`, `Lock`, `SharedLock`, `Insert`, `CheckNotExists`) with assertion accessors and constructors. `OldValue`, `OldValues`, `insert_old_value_if_resolved`, `TxnExtra`, `TxnExtraScheduler`, `WriteBatchFlags`, `LastChange`, and `CommitRole` provide CDC, scheduler, Raft-header, and MVCC read-skip metadata.

## Control Flow
Raw RPC keys are encoded with TiKV byte codec in `Key::from_raw`; timestamped MVCC keys append descending `u64` timestamps so newer versions sort first. Decode helpers validate at least eight timestamp bytes before slicing or decoding. `Mutation::from(kvrpcpb::Mutation)` dispatches on protobuf operation, consuming values where needed and panicking for an unsupported op. Old values are inserted only when resolved, and `LastChange` serializes into two primitive parts where `(0,0)` is unknown, `(0,positive)` is not-exist, and `(positive,positive)` is an existing prior write.

## State and Persistence Behavior
The types are mostly value objects, but their binary representations are persistent storage contracts. `Key` encodes user keys for RocksDB key ordering, timestamp bytes encode MVCC versions, `WriteBatchFlags` bits are carried in Raft request headers, and `LastChange` is serialized into write records elsewhere. `TxnExtra` carries old values and 1PC/flashback flags across scheduling boundaries without owning durable state itself.

## Dependencies and Integration Points
Depends on `tikv_util::codec`, `kvproto::kvrpcpb::Assertion`, `bitflags`, `collections::HashMap`, `farmhash`, and memory sizing traits. It integrates with `timestamp::TimeStamp`, write-record serialization in `write.rs`, MVCC transactions, CDC old-value readers, pessimistic/shared-lock handling, Raft request headers, and log redaction wrappers.

## Risks
Many `Key` methods require the caller to know whether a key is timestamped; misuse can decode garbage or drop user-key bytes. `gen_hash` unwraps raw decoding, so invalid encoded keys panic. `from_bits_check` intentionally panics on unknown Raft flags, which is useful for invariant enforcement but brittle for mixed-version bit rollout. `Mutation::from` panics on unknown operations, and `OldValue::finalized` panics unless unresolved variants have already been materialized.

## Test Signals
The file includes unit tests for flag parsing/panic behavior, timestamp appending, encoded/raw equality, encoded-from checks, old-value resolution, and `LastChange` round trips. Additional useful tests are mixed-version flag compatibility, invalid key encodings, CDC old-value seek paths, and property tests for raw key encode/decode/timestamp ordering.
