# sources/object-store/apache-ozone/hadoop-hdds/docs/themes/ozonedoc/static/swagger-resources/recon-api.yaml

## Purpose
This OpenAPI 3.0 document describes the Apache Ozone Recon REST API exposed under `/api/v1/`. It is a static documentation/specification artifact used by the docs theme, Swagger tooling, client readers, and possibly contract validation. It covers administrative metadata APIs for containers, keys, blocks, namespace state, datanodes, pipelines, Recon tasks, utilization, Prometheus metrics proxying, storage distribution, pending deletion, heatmap features, and manual DB sync utilities.

## Important API surface
- Metadata root: `openapi: 3.0.0`, `info.title: Ozone Recon REST API`, `version: v1`, server URL `/api/v1/`.
- 48 operations are defined across 19 tags.
- Container APIs include listing containers, deleted containers, missing/unhealthy/quasi-closed containers, replica history, mismatch reports, deleted-in-SCM mismatch reports, and keys by container.
- Async unhealthy-container export lifecycle includes listing jobs, starting jobs, checking status, cancelling jobs, and downloading completed TAR archives.
- Volume, bucket, key, and block APIs expose paginated listings and summaries for open keys, multipart open keys, pending-deletion keys/directories, committed key listing under a prefix, and pending block deletion.
- Namespace APIs expose summary, disk usage, quota, and file-size distribution by path.
- Cluster APIs expose cluster state, datanodes, decommissioning information, datanode removal, pipelines, Recon task status, file/container utilization, and Prometheus metrics proxy responses.
- Feature and admin APIs include heatmap read access and health check, disabled feature introspection, OM DB sync trigger, SCM DB snapshot sync trigger/status/cancel, storage distribution, pending deletion by component, and CSV download of datanode storage distribution.
- 60 schemas are defined, including `ContainerMetadata`, `UnhealthyContainerMetadata`, `ListKeysResponse`, `NamespaceMetadataResponse`, `ClusterState`, `DatanodeDetails`, `ExportJob`, `StorageCapacityDistributionResponse`, `DataNodeMetricsServiceResponse`, `EntityReadAccessHeatMap`, and SCM snapshot sync response/status enums.

## Control flow and API behavior
Most endpoints are synchronous GET reads over Recon-maintained metadata, with pagination using cursors such as `prevKey`, `lastKey`, `minContainerId`, and `limit`. Several operations are stateful asynchronous workflows:
- `POST /containers/unhealthy/export` queues an export job for a required unhealthy container state, returning an `ExportJob`; later calls poll `/containers/unhealthy/export/{jobId}`, cancel via DELETE, or download from `/download` after completion. Responses include rate limiting, not-found, conflict, and download-limit cases.
- `GET /pendingDeletion?component=dn` and `GET /storageDistribution/download` may trigger or poll background datanode metrics collection, returning `202` until collection is complete and `200` with JSON or CSV when finished.
- `POST /triggerdbsync/scm/snapshot` starts a one-shot SCM DB snapshot sync with `202` on accepted and `409` if one is already running; status and cancel endpoints expose sync phase, cancellation eligibility, timestamps, and errors.
- Heatmap read access is feature-gated: if disabled, `/heatmap/readaccess` returns `404`, and `/features/disabledFeatures` exposes disabled feature names.

## State and persistence behavior
The spec itself is static YAML, but it documents APIs backed by persistent Recon state: OM/SCM metadata snapshots, Recon DB tables, datanode memory/nodes table, task status, Prometheus metrics, export job files, background metrics collection status, and SCM snapshot sync state. Export jobs persist identifiers, status, timestamps, progress counters, filenames, download counters, and download limits. Snapshot sync status persists current/last status, phase, timestamps, duration, cancellation permission, and last error.

## Dependencies and integration points
The file integrates with Swagger/OpenAPI renderers in the documentation site, Recon server route implementations, Ozone OM/SCM metadata, Prometheus for metrics proxying, HeatMapProvider service for heatmap data, datanodes for storage/pending-deletion metrics, and admin tooling that triggers sync operations. It also depends on OpenAPI clients correctly handling `oneOf`, binary `application/x-tar` and `text/csv` responses, deprecated endpoints, and status codes like `202`, `204`, `400`, `404`, `409`, `429`, `500`, and `503`.

## Schema highlights
- `OpenKeys`, `DeletePendingKeys`, `DeletePendingDirs`, and `ListKeysResponse` carry status and byte-size aggregates alongside lists of OM key information.
- `NamespaceMetadataResponse`, `MetadataDiskUsage`, `MetadataQuota`, and `MetadataSpaceDist` encode namespace statuses such as OK/not found/not applicable through response fields rather than only HTTP status.
- `ClusterState` aggregates container/key/bucket/volume counts, service IDs, datanode health, pipeline count, and storage report details.
- `DataNodeStorageReport`, `ClusterStorageReport`, and `StorageCapacityDistributionResponse` distinguish filesystem capacity, reserved space, Ozone capacity, used/free/committed space, namespace usage, and per-datanode reports.
- `ExportJob` captures queue and download policy with statuses `QUEUED`, `RUNNING`, `COMPLETED`, and `FAILED`.
- `ScmDbSnapshotSyncStatus` is one of `IDLE`, `IN_PROGRESS`, `SUCCESS`, `FAILED`, `CANCELLED`; `ScmDbSnapshotSyncPhase` refines cancellation and progress phases.

## Risks and edge cases
- Many admin-only endpoints expose sensitive metadata or actions; the spec labels them but does not define security schemes, so access control must be enforced by server configuration and implementation.
- Some endpoints return semantic status in JSON bodies while still returning HTTP `200`, which clients must not treat as unconditional success.
- Pagination parameters vary by endpoint (`prevKey`, `lastKey`, `firstKey`, `minContainerId`) and types differ between string and integer; client generators need endpoint-specific handling.
- `/containers/missing` is deprecated in favor of `/containers/unhealthy/MISSING`; clients should migrate.
- Binary responses (`application/x-tar`, `text/csv`) require separate client handling from JSON endpoints.
- Background task endpoints can return `202` and nullable result arrays; clients must poll and tolerate incomplete data.
- OpenAPI schema coverage includes broad object maps and loosely typed fields, so generated clients may not fully enforce server contracts.

## Test signals
Validate the YAML with an OpenAPI 3 parser and render it through the docs Swagger UI. Contract tests should compare documented paths, operation IDs, parameters, response codes, and schema fields with Recon server route implementations. Client behavior tests should cover pagination, deprecated missing-container replacement, invalid parameters (`400`/`406`), export job lifecycle including `429` and `409`, heatmap disabled `404`, pending-deletion `202` polling, SCM snapshot sync `202`/`409`/cancel behavior, binary download content types, and `503` while Recon is bootstrapping OM DB.
