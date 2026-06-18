# sources/object-store/minio-mc/cmd/health_v1.go

Purpose: Maps `madmin.HealthInfoV0` into mc's v1 cluster health report schema.

Important APIs/types/functions: hardware/software structs, `ClusterHealthV1`, `String`, `JSON`, getters, `MapHealthInfoToV1`, `parallelize`, `addKeysToSet`, and map helpers for CPU, drives, memory, network, and drive performance.

Control flow: `MapHealthInfoToV1` returns error status when input error is non-nil. Otherwise it maps subsystem data in parallel, builds a server address set from all maps, merges hardware per server, and copies MinIO software/config/process/OS fields.

State and persistence: Pure data transformation; no persistence.

Dependencies/integration: Uses `madmin-go`, `gopsutil`, MinIO set, reflect map keys, and JSON output.

Risks: Iterating a set/map produces nondeterministic server order. `parallelize` defers `Wait`, which works but is unusual. Missing data yields zero-value nested structs.

Test signals: No direct tests.
