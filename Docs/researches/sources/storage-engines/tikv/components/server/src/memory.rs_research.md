## sources/storage-engines/tikv/components/server/src/memory.rs

Purpose: flushes hierarchical memory trace providers into TiKV memory trace prometheus gauges.

Important APIs/types/functions: `MemoryTraceManager`, `flush`, and `register_provider`. Providers are `Arc<MemoryTrace>` roots.

Control flow: `flush` iterates registered providers, then each child and optional leaf. Leafless children emit `provider-child`; leaf children emit `provider-child-leaf`; provider totals emit `provider`.

State/persistence: holds an in-memory vector of providers. Metrics are updated each flush; no durable persistence.

Dependencies/integration: used by server metrics flusher with raftstore and coprocessor memory trace roots. Depends on `tikv_alloc::trace::MemoryTrace`, `tikv::server::MEM_TRACE_SUM_GAUGE`, and `tikv_util::time::Instant`.

Risks: labels are constructed dynamically and can grow with provider topology; `_now` is currently unused; only two child levels are represented.

Test signals: no direct tests; exercised through server metrics-flush integration.
