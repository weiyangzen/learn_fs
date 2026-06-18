# sources/storage-engines/tikv/components/engine_traits/src/errors.rs

Purpose: Provides the common engine error/status type shared by all engine implementations and TiKV callers.

Important APIs and control flow: `Code`, `SubCode`, and `Severity` mirror RocksDB-like status fields. `Status` stores those fields plus string state and exposes builder/getter methods. `Error` wraps engine status plus range, protobuf, IO, boxed, CF, codec, Raft log availability, compaction, and boundary errors. `ErrorCodeExt` maps variants to TiKV error codes, and conversions to Raft error and string are provided.

State, persistence, and dependencies: Error values are transient but encode persistent failure conditions such as IO, corruption, compaction, or missing entries. Dependencies include `error_code`, `raft`, `protobuf`, `thiserror`, and TiKV log wrappers.

Integration points, risks, and test signals: Used by every trait result. Risks include losing backend-specific detail inside `Status`, conflating storage and Raft errors, accidental panics from formatted keys, and changing error-code mappings that affect observability. Shared tests assert engine errors for invalid operations; Raft integrations rely on the special compaction/unavailable conversions.
