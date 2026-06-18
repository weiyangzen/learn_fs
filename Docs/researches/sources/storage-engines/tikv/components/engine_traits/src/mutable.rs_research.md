# sources/storage-engines/tikv/components/engine_traits/src/mutable.rs

Purpose: Defines synchronous mutation methods for engines.

Important APIs and control flow: `SyncMutable` provides put, put-CF, delete, delete-CF, delete-range, delete-range-CF, plus protobuf helpers that serialize messages before writing.

State, persistence, and dependencies: Implementations apply changes directly to persistent engine state or WAL/memtable state according to backend semantics.

Integration points, risks, and test signals: Used by direct write paths and tests as the default-CF counterpart to write-batch mutation. Risks include range-delete bound semantics, CF validation, protobuf serialization errors, and snapshot visibility expectations. Shared scenario tests cover all direct mutation variants and range-delete edge cases.
