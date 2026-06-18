<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/healthcheck-handler.go -->
# sources/object-store/minio/cmd/healthcheck-handler.go

## Purpose
Implements Kubernetes/operator-facing health endpoints for cluster write quorum, cluster read quorum, readiness, and liveness. It separates external dependency readiness from basic process liveness.

## Important APIs, types, and functions
- `checkHealth` validates object layer, bucket metadata system, and IAM system initialization.
- `ClusterCheckHandler` reports write health and maintenance drain status.
- `ClusterReadCheckHandler` reports read health.
- `ReadinessCheckHandler` checks initialization, peer-call bypass, request queue pressure, KMS key generation, and etcd reachability.
- `LivenessCheckHandler` checks initialization and request queue pressure without external systems.

## Control flow
Cluster handlers build a request context with the configured cluster deadline, call `objLayer.Health` with maintenance/deployment options from query parameters, set quorum/storage-class/healing headers, and return OK, service unavailable, or precondition failed for maintenance. Readiness and liveness mark server status if the object layer is missing, allow internode peer calls, return busy when queued requests exceed capacity, and readiness additionally verifies KMS and etcd with timeouts.

## State and persistence behavior
No durable state. Handlers read global object layer, IAM/bucket metadata init state, API config, HTTP queue stats, KMS, and etcd client. They write response status and MinIO-specific health headers.

## Dependencies and integration points
Integrates health routes, object-layer `Health`, global API deadlines, KMS `GenerateKey`, etcd `Get`, MinIO API error conversion, request queue stats, and internal peer-call headers.

## Risks and edge cases
Readiness can fail due to external KMS/etcd even when the server process is alive; liveness intentionally avoids those calls to prevent restart loops. Queue-pressure comparison depends on request pool capacity and can behave oddly if capacity is zero. Cluster maintenance uses 412 to tell orchestrators a node should not be removed.

## Test signals
No direct tests in this group. Expected signals include HTTP status codes/headers for healthy/unhealthy quorum, KMS/etcd failures, peer calls, busy queues, GET vs HEAD response shapes, and maintenance precondition behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/healthcheck-handler.go -->
