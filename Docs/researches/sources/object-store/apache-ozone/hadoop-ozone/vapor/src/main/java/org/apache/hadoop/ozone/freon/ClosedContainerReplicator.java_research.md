# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/ClosedContainerReplicator.java

## Purpose
Vapor command that downloads/imports closed containers using datanode replication code, mainly for replication performance and behavior testing.

## Important APIs, types, and functions
Command `cr`/`container-replicator`, option `--datanode`. Uses `ContainerOperationClient`, `ContainerInfo`, `Pipeline`, `ReplicationTask`, `ReplicateContainerCommand`, `ReplicationSupervisor`, `DownloadAndImportReplicator`, `ContainerImporter`, `SimpleContainerDownloader`, `ContainerSet`, handlers, volume sets, container metadata store, and metrics timer.

## Control flow
`replicate` validates destination storage directories are empty, lists up to one million containers from SCM, initializes a fake datanode replication supervisor/controller/importer stack, builds tasks for closed containers optionally filtered by source datanode UUID, sets Freon test count to task count, then runs each task through `ReplicationSupervisor.TaskRunner`.

## State and persistence behavior
Writes imported container data into configured datanode storage directories and opens a witnessed container metadata store. It refuses non-empty destination directories to avoid clobbering existing data.

## Dependencies and integration points
Deeply integrates SCM container listing/pipelines, datanode volume initialization, schema V3 DB loading, container handlers, replication downloader/importer, and Freon metrics.

## Risks and edge cases
Destination emptiness is mandatory. Queue size is based on container count. Fake datanode IDs and random SCM/cluster IDs may affect metadata compatibility. Only CLOSED containers are replicated.

## Test signals
No direct tests. Signals are task count, `replicate-container` timing, successful imports, and supervisor counters.
