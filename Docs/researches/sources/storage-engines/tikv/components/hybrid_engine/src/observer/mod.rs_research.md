# sources/storage-engines/tikv/components/hybrid_engine/src/observer/mod.rs

Purpose: module hub for hybrid engine observers.

Important APIs/types/functions: declares `load_eviction`, `snapshot`, `write_batch`, test-only `test_write_batch`; re-exports observer types and snapshot pin.

Control flow: no runtime behavior.

State and persistence: none.

Dependencies/integration: provides the public observer registration surface for raftstore integration.

Risks: re-exported names are the compatibility surface if observer modules are moved.

Test signals: includes write-batch tests under `cfg(test)`.
