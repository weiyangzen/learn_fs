# sources/storage-engines/foundationdb/fdbserver/kvstore/RocksDBCommon.cpp

## Purpose
This file implements small shared RocksDB helpers used by multiple FoundationDB RocksDB-backed kvstores. It centralizes `StringRef`/`rocksdb::Slice` conversion and maps integer knobs to RocksDB enum values with trace warnings for invalid configuration.

## Important APIs, Types, And Functions
`RocksDBCommon::toSlice` wraps a `StringRef` byte span as a RocksDB `Slice` without copying. `toStringRef` wraps a RocksDB `Slice` as `StringRef` without copying. `getErrorReason` converts `rocksdb::BackgroundErrorReason` to a string containing both the numeric reason and readable label. `getWalRecoveryModeFromKnob` maps knob values 0 to 3 to RocksDB WAL recovery modes. `getWalRecoveryMode` reads `SERVER_KNOBS->ROCKSDB_WAL_RECOVERY_MODE`. `getCompactionPriorityFromKnob` maps values 0 to 4 to `rocksdb::CompactionPri`. `getIndexTypeFromKnob` maps values 0 to 3 to `BlockBasedTableOptions::IndexType`.

## Control Flow
All enum helpers are switch statements. Invalid WAL recovery mode logs `InvalidWalRecoveryMode` and defaults to point-in-time recovery. Invalid compaction priority logs `InvalidCompactionPriority` and defaults to `kMinOverlappingRatio`. Invalid index type logs `InvalidIndexType` and defaults to binary search.

## State And Persistence Behavior
This file has no retained state and no persistence. Conversion helpers return non-owning views; caller-owned memory must outlive the RocksDB or FDB view consumer.

## Dependencies And Integration Points
The implementation is compiled only under `WITH_ROCKSDB`. It depends on `RocksDBCommon.h`, `fdbserver/core/Knobs.h`, `flow/Trace.h`, and RocksDB option/listener/table headers. It is used by sharded RocksDB and other RocksDB storage engine code to avoid duplicating knob decoding.

## Risks
The non-copying conversions are easy to misuse if the source slice is temporary. The background error reason switch must track RocksDB enum additions; unknown values degrade to an "Unknown" string. Defaults on invalid knob values keep the process running, but may hide misconfiguration unless trace events are monitored.

## Test Signals
Unit tests should verify every knob value maps to the expected RocksDB enum, invalid values log and choose documented defaults, conversion helpers preserve binary bytes including embedded nulls, and callers do not retain converted views past source lifetime.
