# sources/storage-engines/tikv/components/hybrid_engine/src/lib.rs

Purpose: crate root and public surface for hybrid engine components.

Important APIs/types/functions: declares modules and re-exports `HybridEngine` and `HybridEngineSnapshot`; exposes `observer` and `util`.

Control flow: none. A TODO notes the crate is now a thin shim and may be merged into `in_memory_engine`.

State and persistence: none.

Dependencies/integration: consumers import hybrid engine types and observer registrations through this root.

Risks: moving or merging this shim requires import-path migration.

Test signals: module tests compile through this crate root.
