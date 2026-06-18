# sources/object-store/minio/cmd/metrics-v3-system-network.go

Purpose: Exposes v3 internode network metrics for distributed erasure deployments.

Important APIs/types/functions: Defines `internodeErrorsTotal`, `internodeDialErrorsTotal`, `internodeDialAvgTimeNanos`, `internodeSentBytesTotal`, and `internodeRecvBytesTotal` descriptors. `loadNetworkInternodeMetrics` populates them.

Control flow: The loader reads connection stats from `globalConnStats.toServerConnStats()` and RPC stats from `rest.GetRPCStats()`. It emits metrics only if `globalIsDistErasure` is true.

State and persistence behavior: Stateless over process-global connection and RPC counters. The emitted counters are process lifetime values and dial average is a live aggregate.

Dependencies and integration points: Depends on `globalConnStats`, `globalIsDistErasure`, and internal REST RPC stats. It complements API traffic metrics, which cover S3 bytes.

Risks: Single-node or non-distributed configurations emit no internode series, so dashboards must tolerate absent metrics. Dial average duration is converted directly to float64 nanoseconds; naming makes units clear but consumers must not treat it as seconds.

Test signals: No direct tests in this subset.
