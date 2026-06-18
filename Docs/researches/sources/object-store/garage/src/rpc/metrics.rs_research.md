# sources/object-store/garage/src/rpc/metrics.rs

Purpose: OpenTelemetry metrics for outbound RPC behavior.

Important APIs and types: `RpcMetrics` owns counters for emitted RPCs, timeouts, NetApp communication errors, Garage handler errors, and a duration recorder. `RpcMetrics::new` registers instruments under meter `garage_rpc`.

Control flow: construction initializes instruments. Recording happens in `rpc_helper.rs`, where each call increments `rpc_counter`, records duration, and increments timeout/network/Garage error counters according to outcome.

State and persistence: metric instruments are runtime observers/counters only; no persistence.

Dependencies and integration: depends on `opentelemetry::{global, metrics::*}`. `RpcHelperInner` stores one `RpcMetrics` instance and attaches endpoint/from/to tags while recording.

Risks and test signals: metric naming and cardinality matter. Tags include node IDs and endpoints, which are useful but can grow with cluster size. The file comment incorrectly says `TableMetrics`, a naming drift risk. No direct tests; observability is validated by runtime metrics export.
