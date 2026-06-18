# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/GrvProxyInterface.h

Purpose: Defines the GRV proxy RPC contract for read-version acquisition, health metrics, and global configuration refreshes.

Important APIs/types/functions: `GetReadVersionReply` extends `BasicLoadBalancedReply` with version, locked flag, metadata version, mid-shard size, ratekeeper throttled flags, tag throttle info, storage-server version vector delta, and proxy id. `GetReadVersionRequest` carries span context, transaction count, priority flags, transaction priority, tags, debug id, reply, client max version-vector version, and optional max GRV queue delay. Priority is encoded into high bits of `flags`. `GetHealthMetricsReply/Request` serialize health metrics through a binary string to avoid direct field compatibility issues. `GlobalConfigRefreshReply/Request` return a range result and version for global config state. `GrvProxyInterface` serializes process id, provisional flag, and the primary `getConsistentReadVersion` stream, reconstructing wait-failure, health metrics, and refresh streams as adjusted endpoints.

Control flow: Clients batch or send GRV requests to `getConsistentReadVersion`; deserialization recovers priority from flags. Replies update cached read versions, tag throttles, ratekeeper state, health metrics, and version-vector caches. Global config code asks GRV proxies for refreshes from a last-known version.

State and persistence behavior: Interface state is wire/transient. Health metrics reply stores a serialized binary copy and reconstructs `HealthMetrics` on deserialization. Global config refresh data mirrors persistent global config keyspace but is transported through GRV proxies.

Dependencies and integration points: Depends on tag throttling, version vectors, Flow file identifiers/RPC/load balancing/stats/timed requests, and FDB types. Integrated with `DatabaseContext` GRV batching, ratekeeper throttling, health/status, global config, and commit-proxy client info.

Risks: Priority flag masks overlap by design; incorrect masking can downgrade system-immediate requests. Adjusted endpoint numbering must remain stable. `proxyId` is used to detect stale GRV proxies. Version-vector maxVersion/delta handling affects causal read correctness. Health metrics binary serialization must stay compatible with `IncludeVersion()`.

Test signals: GRV priority encode/decode; tagged and untagged request serialization; ratekeeper throttled reply handling; tag throttle updates; version-vector delta cache updates; health metrics detailed/non-detailed serialization; global config refresh; adjusted endpoint reconstruction.
