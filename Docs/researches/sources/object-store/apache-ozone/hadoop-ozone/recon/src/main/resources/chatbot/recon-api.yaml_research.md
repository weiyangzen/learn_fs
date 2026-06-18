# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/chatbot/recon-api.yaml

Purpose: `recon-api.yaml` is the OpenAPI 3.0 contract used by the Recon chatbot/resource layer to describe the Ozone Recon REST API. It documents endpoint paths, query parameters, operation ids, response schemas, and sample payloads for containers, keys, namespace metadata, cluster state, datanodes, pipelines, tasks, utilization, and metrics.

Important APIs and types: top-level server URL is `/api/v1/`. Tags group endpoints by domain. Major paths include `/containers`, `/containers/deleted`, `/containers/missing`, `/containers/unhealthy`, `/containers/mismatch`, `/volumes`, `/buckets`, `/keys/open`, `/keys/deletePending`, `/keys/listKeys`, `/containers/{id}/keys`, `/blocks/deletePending`, `/namespace/summary`, `/namespace/usage`, `/namespace/quota`, `/namespace/dist`, `/clusterState`, `/datanodes`, `/datanodes/remove`, `/pipelines`, `/task/status`, `/utilization/fileCount`, `/utilization/containerCount`, and `/metrics/query`. Components define schemas such as `ContainerMetadata`, `DeletedContainers`, `OpenKeys`, `ListKeysResponse`, `DeletePendingKeys`, `NamespaceMetadataResponse`, `MetadataDiskUsage`, `ClusterState`, `DatanodesSummary`, `PipelinesSummary`, `TasksStatus`, and `MetricsQuery`.

Control flow and integration: this file is declarative. Generated clients, chatbot tooling, documentation, or validation layers can use `operationId` values to map user intents or API calls to Recon endpoints. It mirrors server-side resources elsewhere in Recon and should evolve with REST resource signatures.

State and persistence: no runtime state. It describes persisted/derived Recon data returned by REST resources, including OM metadata, SCM state, Recon SQL tables, and Prometheus proxy output.

Dependencies: OpenAPI 3.0 tooling and JSON schema consumers.

Risks and test signals: several schema examples and field names should be linted, including odd example keys such as `isKey"` in `MetadataDiskUsage`, nested `ClusterStorageReport` indentation under `DataNodeStorageReport`, and inconsistent integer/string typing for prefix parameters. Contract tests should validate the YAML, compare documented paths with JAX-RS resources, and exercise pagination, filtering, and error responses for 400 and 503 cases.
