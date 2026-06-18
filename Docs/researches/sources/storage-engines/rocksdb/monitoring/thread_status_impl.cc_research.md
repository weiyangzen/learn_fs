# sources/storage-engines/rocksdb/monitoring/thread_status_impl.cc

Purpose: Implements public `ThreadStatus` formatting and operation-property interpretation helpers, with disabled stubs under `NROCKSDB_THREAD_STATUS`.

Important APIs/types/functions: Defines `ThreadStatus::kEnabled`, `GetThreadTypeName`, `GetOperationName`, `GetOperationStageName`, `GetStateName`, `MicrosToString`, `GetOperationPropertyName`, and `InterpretOperationProperties`.

Control flow: Name helpers range-check enum values and return entries from global operation/stage/state tables or unknown names. `MicrosToString` returns empty for zero and otherwise delegates to `AppendHumanMicros`. `InterpretOperationProperties` emits maps for compaction and flush properties, splitting compaction input/output level and flag bitfields into named values.

State and dependencies: No mutable state here; it reads global metadata from `util/thread_operation.h`. Depends on `rocksdb/env.h`, `rocksdb/thread_status.h`, and string utilities.

Risks/test signals: Disabled builds return empty strings/maps and `kEnabled=false`, so callers must tolerate missing status names. Property interpretation is operation-specific; unknown operations intentionally produce no properties.
