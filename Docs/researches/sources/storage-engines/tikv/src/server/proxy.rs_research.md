# sources/storage-engines/tikv/src/server/proxy.rs

Purpose: implements gRPC forwarding support so one TiKV node can receive a client RPC and forward it to another TiKV address identified by request metadata.

Important APIs/types/functions: `get_target_address` reads forwarding metadata; `build_forward_option` creates call options with that metadata; `Proxy::new` and `Proxy::call_on` manage forwarding clients; `forward_unary!` and `forward_duplex!` macros redirect service handlers.

Control flow: service macros inspect request metadata and return early if forwarding is requested. `Proxy::call_on` gets or creates a per-address pooled client, waits up to three seconds for channel connectivity, then invokes the supplied callback. Unary forwarding maps async client result to original response sink; duplex forwarding bridges request and response streams with batching enabled.

State and persistence: proxy state is an in-memory map from target address to a round-robin `ClientPool`. Cloned proxies share security/config/env references but start with an empty pool. No durable state.

Dependencies and integration: depends on gRPC channels/call options, `TikvClient`, `SecurityManager`, server `Config`, and proxy metrics from server metrics. Service implementations can use the exported macros.

Risks: forwarded target metadata must be valid UTF-8 and ASCII when built. Pools are never pruned, so long-lived nodes forwarding to many addresses may retain clients. If the weak gRPC environment cannot be upgraded or connection is not ready within three seconds, the callback is skipped without a response written by this layer.

Test signals: no local tests; macro behavior is covered by service-level integration paths.
