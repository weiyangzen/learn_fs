# sources/storage-engines/tikv/src/coprocessor/readpool_impl.rs

Purpose: builds coprocessor Yatp future pools with proper thread-local engine setup and metric flushing.

Important APIs/types: `FuturePoolTicker<R>` implements `PoolTicker::on_tick` by calling `tls_flush(&reporter)`. `build_read_pool` converts `CoprReadPoolConfig` into three Yatp configs named `cop-low`, `cop-normal`, and `cop-high`; each pool sets TLS engine and foreground read I/O type on worker start, destroys TLS engine on stop, and uses the metric flushing ticker. `build_read_pool_for_test` builds equivalent pools with `DefaultTicker`.

State and persistence: thread-local engine and I/O type are set per worker. Metrics are flushed through the reporter; no durable state is written. Dependencies include file-system I/O type markers, Yatp pool builder, coprocessor metrics, and TiKV engine/TLS helpers.

Integration points: server initialization uses this to create read pools consumed by `Endpoint`; tests use the test builder. Risks include config length assumptions (`assert_eq!(configs.len(), 3)`), holding cloned engines behind `Arc<Mutex<_>>` during setup, and missing TLS engine setup causing unsafe endpoint snapshot calls to fail. Test signal is indirect through many endpoint tests using `build_read_pool_for_test`.
