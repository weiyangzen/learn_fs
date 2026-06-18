# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/DownloadAndImportReplicator.java

Purpose: implements pull replication by downloading a container archive from source datanodes and importing it locally.

Important APIs and functions: `replicate(ReplicationTask)` skips if the container is already present, reads the configured `CopyContainerCompression`, chooses a target volume using default replication space, downloads into that volume's `container-copy/tmp` directory through `ContainerDownloader`, records downloaded byte size, invokes `ContainerImporter.importContainer`, and sets task status to `DONE` or `FAILED`.

Control flow and state: the method is synchronous and runs inside the replication supervisor executor. It reserves space through `chooseNextVolume`; in `finally`, it decrements committed bytes by default replication space if a volume was selected. Download failure returning null marks the task failed without import.

Dependencies and integration: coordinates `ContainerSet`, `ContainerImporter`, `ContainerDownloader`, `HddsVolume`, and compression config. It is selected for replicate-from-sources commands.

Risks and test signals: the reservation decrement currently uses default space even when actual container size support exists elsewhere; tests should verify reservation balance, source retry behavior, existing-container skip, tarball cleanup delegated to importer, transferred byte accounting, and IO exception handling.
