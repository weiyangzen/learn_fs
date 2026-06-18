# sources/storage-engines/rocksdb/include/rocksdb/port_defs.h

Purpose: This header holds small common definitions shared by RocksDB porting code, public API headers, and internal directories.

Important APIs and types: It forward-declares `port::CondVar` and defines `enum class CpuPriority` with `kIdle`, `kLow`, `kNormal`, and `kHigh`.

Control flow: There is no executable control flow. The enum is consumed by scheduling or thread/CPU-priority integration code elsewhere.

State and persistence behavior: It defines no state and has no persistence effect. CPU priority is a runtime scheduling hint when used by implementations.

Dependencies and integration points: It depends only on `rocksdb_namespace.h`. Port implementations, Env/threading code, and public APIs can include it without pulling in heavier platform headers.

Risks and edge cases: The enum's numeric values are part of cross-component assumptions if serialized, logged, or mapped to OS priorities. Platform-specific code must handle unsupported priority changes gracefully.

Test signals: Compile tests should verify low dependency weight. Port tests should validate mappings from `CpuPriority` to actual platform priority behavior where implemented.
