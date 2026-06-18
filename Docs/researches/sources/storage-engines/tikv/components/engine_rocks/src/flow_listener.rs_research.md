<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/flow_listener.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/flow_listener.rs

Purpose: sends storage-flow events derived from RocksDB flush, ingestion, compaction, tablet creation, and tablet destruction.

Important APIs/types/functions: `FlowInfo`, `FlowListener::{new, clone_with, on_created, on_destroyed}`, and `EventListener` callbacks.

Control flow: flush and L0 ingestion compute table data/index/filter bytes and send `Flush`. Non-L0 ingestion sends `Compaction`. Completed compactions distinguish L0-to-non-L0, L0 intra-compaction, and generic compaction events, computing input or reclaimed bytes from table properties and file sets.

State and persistence behavior: maintains a shared channel sender and a region id tag; emits runtime accounting events but does not persist state directly.

Dependencies/integration: consumed by TiKV flow control logic and tablet lifecycle code; depends on RocksDB event metadata and `collections::hash_set_with_capacity`.

Risks: send failures are ignored, so downstream flow accounting can silently miss events. File-name conversion failures skip individual files. Failed compactions are ignored.

Test signals: no direct tests in this file; behavior is typically observed through flow-control integration tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/flow_listener.rs -->
