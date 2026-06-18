# sources/storage-engines/rocksdb/trace_replay/trace_record_handler.cc

## Purpose

Implements `TraceExecutionHandler`, the DB-backed handler that replays decoded query trace records against a live RocksDB instance and optionally returns execution results with timing and values.

## Important APIs, Control Flow, And Dependencies

The constructor builds a map from column-family ID to `ColumnFamilyHandle*` and grabs the DB system clock. Write handling reconstructs a `WriteBatch` from the trace payload and calls `DB::Write`. Get handling validates CF ID, performs `DB::Get`, treats `NotFound` as replay-success, and returns a `SingleValueTraceExecutionResult` with the actual status/value. Iterator handling applies optional lower/upper bounds to `ReadOptions`, creates an iterator, performs `Seek` or `SeekForPrev`, captures key/value when valid, deletes the iterator, and returns its status. MultiGet handling validates CF IDs and vector sizes, calls `DB::MultiGet`, treats per-key `NotFound` as OK for replay, and returns all statuses/values.

## State, Persistence, Integration, Risks, And Test Signals

The handler holds a non-owning DB pointer, non-owning CF handles, default write/read options, and a CF lookup map. Replay mutates persistent DB state for write records and reads persistent state for get/iterator/multiget records. Dependencies include `rocksdb/db.h`, iterators, write batches, status/result classes, and `SystemClock`. Risks include stale CF handles, non-ownership/lifetime assumptions, iterator bound slices pointing to record-owned memory only for the duration of the call, and replay semantics that suppress `NotFound` errors while preserving them in result objects. Tests exercise this path indirectly through trace replay users rather than this file alone.
