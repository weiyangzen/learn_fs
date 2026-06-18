## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/StorageContainerServiceProvider.java

Purpose: this SPI abstracts Recon's RPC access to authoritative SCM state.

Important APIs and types: exposes pipeline listing/lookup, single and batched container-with-pipeline lookup, SCM node listing, total and per-state container counts, SCM DB snapshot retrieval, ID-only paginated container listing by lifecycle state, and full `ContainerInfo` paginated listing by state. Key types include `Pipeline`, `ContainerWithPipeline`, `ContainerID`, `ContainerInfo`, `HddsProtos.Node`, lifecycle states, and `DBCheckpoint`.

Control flow: Recon managers call this SPI when they need SCM as source of truth: startup pipeline initialization, report-time container/pipeline backfill, dead-node state verification, full SCM DB snapshot refresh, and targeted container sync.

State and persistence: the interface owns no state. Implementations talk to SCM and may materialize downloaded DB checkpoints on local disk.

Dependencies and integration points: implemented by `StorageContainerServiceProviderImpl` outside this subset and bound by `ReconControllerModule`. Heavily used by `ReconStorageContainerManagerFacade`, `ReconStorageContainerSyncHelper`, `ReconContainerManager`, `ReconPipelineReportHandler`, and `ReconDeadNodeHandler`.

Risks and edge cases: call semantics differ by payload size: ID-only APIs are intended for hot-path pagination, while full info/CWP APIs are targeted. `getSCMDBSnapshot` returns nullable checkpoint without throwing checked exceptions, so callers must validate. Batch CWP lookup can omit containers whose pipelines cannot be resolved, requiring fallback logic for non-OPEN states.

Test signals: SCM sync tests should mock this interface extensively for counts, pages, batch omissions, snapshots, and exceptions. Contract tests for the implementation should verify pagination inclusivity and lifecycle filtering.
