# sources/object-store/minio/cmd/callhome.go

## Purpose
`callhome.go` implements MinIO's optional SUBNET callhome diagnostics loop. It elects one cluster node with a namespace lock, collects `madmin.HealthInfo`, gzip-compresses it, uploads it to SUBNET, and emits internal audit/log signals for each diagnostics attempt.

## Important APIs, Types, And Functions
`initCallhome` starts the background loop only when `globalCallhomeConfig.Enabled()` is true. `runCallhome` acquires `.minio.sys/callhome/runCallhome.lock` using `ObjectLayer.NewNSLock` and keeps the elected node running periodic calls. `performCallhome` builds a health query for all `madmin.HealthDataTypesList`, calls `fetchHealthInfo`, and sends the final report. `sendHealthInfo` uploads to `globalSubnetConfig.BaseURL + /api/health/upload`. `createHealthJSONGzip` writes a version header and health payload into a gzip JSON stream.

## Control Flow
The startup goroutine repeatedly tries `runCallhome`; a lock timeout means another node is leader, so it sleeps a randomized fraction of the configured frequency and retries. The leader performs one immediate callhome, then ticks on `globalCallhomeConfig.FrequencyDur()` until disabled or canceled. `performCallhome` uses a ten-second health collection context and returns silently on timeout.

## State And Persistence Behavior
The file does not persist local state. Cluster coordination is transient lock state in the object namespace. Uploaded diagnostics leave MinIO via `globalSubnetConfig.Upload`. Audit state is written through `auditLogInternal`.

## Dependencies And Integration Points
It depends on object-layer readiness, SUBNET configuration, callhome dynamic configuration from `config-current.go`, health collection helpers, namespace locks, internal logging, and madmin health schemas.

## Risks And Test Signals
Risks include silent skipped uploads when the object layer is unavailable, upload failures only logged/audited, and gzip helpers returning nil after encode errors. The lock path is critical for one-leader behavior. No direct tests are in this subset; coverage is mostly integration-level through config enablement, health collection, and SUBNET upload behavior.
