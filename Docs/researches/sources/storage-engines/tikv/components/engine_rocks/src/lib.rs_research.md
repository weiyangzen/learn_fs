<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/lib.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/lib.rs

Purpose: crate root for TiKV's RocksDB engine implementation and public re-export surface.

Important APIs/types/functions: module declarations, broad `pub use` exports, raw RocksDB perf exports, `flow_control_factors`, `raw`, and crate-level `get_env`.

Control flow: compile-time module wiring mirrors `engine_traits`; `get_env` first applies optional encryption env wrapping, then applies file-system inspection/rate limiting and returns a RocksDB env.

State and persistence behavior: no direct durable state, but exported modules implement persistence. Env composition determines encryption and IO-limiter behavior for future DB file operations.

Dependencies/integration: central integration point for downstream TiKV crates; exposes both abstraction implementations and selected raw RocksDB APIs during ongoing engine abstraction migration.

Risks: broad re-exports can leak raw RocksDB types and make abstraction boundaries harder to enforce. Env wrapper order is significant: encryption wraps base env before file-system inspection.

Test signals: no direct tests; all sibling module tests compile through this crate root.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/lib.rs -->
