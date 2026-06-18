# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestEndpoints.java

## Purpose
Broad Recon API endpoint test suite covering node, pipeline, Prometheus metrics proxy, cluster state, utilization histograms, volume listing, bucket listing, datanode removal, and decommission status APIs. It builds an in-process Recon test injector backed by temporary OM metadata, Recon SQL state, container DB state, and a Recon SCM facade, then asserts that endpoint DTOs reflect seeded SCM/OM/task state.

## Important APIs, types, and functions
- Endpoints under test: `NodeEndpoint`, `PipelineEndpoint`, `ClusterStateEndpoint`, `UtilizationEndpoint`, `MetricsProxyEndpoint`, `VolumeEndpoint`, and `BucketEndpoint`.
- Fixture construction uses `ReconTestInjector`, `ReconOMMetadataManager`, `ReconStorageContainerManagerFacade`, `ReconPipelineManager`, `ReconFileMetadataManager`, `ReconGlobalStatsManager`, `ContainerHealthSchemaManager`, and jOOQ `DSLContext`.
- Task integrations include `FileSizeCountTaskFSO`, `FileSizeCountTaskOBS`, `ContainerSizeCountTask`, and `OmTableInsightTask`.
- Helper assertions `testDatanodeResponse`, `testVolumeResponse`, and `testBucketResponse` validate endpoint DTO fields, ACL grouping, storage reports, layout versions, quotas, and bucket layouts.
- `waitAndCheckConditionAfterHeartbeat` sends a synthetic SCM heartbeat with container report data and waits until asynchronous event processing has materialized container counts.

## Control flow
`initializeInjector` is run once per test instance and creates random datanodes with stable host/IP values, a one-node pipeline, container-with-pipeline lookup mocks, a mocked Prometheus HTTP call, Guice bindings, endpoint instances, utilization tasks, and a pipeline entry in `ReconPipelineManager`. Each `setUp` registers three datanodes with storage, node, container, and pipeline reports, processes the event queue, adds a second sample volume plus two buckets with ACL/quota/storage metadata, writes three live keys and deleted-key/deleted-directory records, then truncates global stats so each test controls OM table insight results.

Individual tests read endpoint responses and assert exact DTO behavior: datanodes and operational-state changes; pipeline metadata and later container count convergence; Prometheus response streaming; cluster state before and after OM table insight reprocess; file/container size histogram writes and query filters; volume/bucket pagination; explicit datanode removal failure buckets; and decommission status maps assembled from mocked SCM node queries, container-on-decommissioning-node maps, and JSON metrics.

## State and persistence behavior
The suite persists OM metadata in temporary RocksDB-backed managers, Recon global stats in SQL, file-size counts in Recon file metadata storage, container size counts through the SCM facade DAO, and SCM node/pipeline/container state in the in-process Recon SCM facade. The tests deliberately mix synchronous table writes with asynchronous SCM heartbeat/event processing, so some assertions use wait loops after sending a heartbeat. Global stats are truncated between tests because `ClusterStateEndpoint` reads counts from the SQL-backed global stats manager after `OmTableInsightTask` reprocesses OM tables.

## Dependencies and integration points
This file is a high-coverage integration point between Recon REST resources, OM metadata tables, Recon SQL/jOOQ schema definitions, Recon SCM facade components, SCM datanode protocol registration/heartbeat handling, Prometheus proxy plumbing, and task-generated utilization/global-stat data. It also exercises ACL aggregation into API metadata and decommission status translation from SCM protocol and metrics JSON into Recon response maps.

## Risks and edge cases
The suite is sensitive to asynchronous event timing for heartbeat/container processing, exact storage arithmetic, and DTO ordering assumptions in pagination tests. It uses broad in-process state that can leak across tests if setup guards or table truncation change. The mocked Prometheus and SCM decommission JSON strings are narrow and may miss malformed or partially populated production responses. Removal tests currently assert failure paths for decommissioned, non-DEAD, and unknown nodes; they do not prove a successful physical removal of a DEAD node.

## Test signals
Strong signals include exact datanode storage totals, layout versions, operational-state propagation, pipeline leader/count fields, byte-for-byte metrics proxy output, cluster state counts before and after task reprocess, RocksDB histogram bins, endpoint filter results, volume/bucket ACL/quota/layout DTOs, and decommission response container/metric buckets. Failures usually identify a contract change in endpoint DTOs, Recon task output, or SCM/OM state projection.
