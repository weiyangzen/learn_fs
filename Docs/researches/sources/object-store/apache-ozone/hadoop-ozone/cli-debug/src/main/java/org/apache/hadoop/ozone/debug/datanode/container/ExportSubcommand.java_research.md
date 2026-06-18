# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/container/ExportSubcommand.java

Purpose: `ExportSubcommand` exports one or more local container replicas to tar files.

Important APIs and types: It implements `Callable<Void>`, uses parent `ContainerCommands`, `OnDemandContainerReplicationSource`, `ContainerReplicationSource`, `StorageContainerException`, and `CopyContainerCompression.NO_COMPRESSION`.

Control flow: The command loads containers from volumes, creates a replication source from the parent controller, then loops from the requested container ID for `--count` containers. It prepares each container, opens `container-<id>.tar` under `--dest`, copies data, ignores `CONTAINER_NOT_FOUND`, logs success, and increments the ID.

State and persistence behavior: It reads local container metadata/chunks and writes tar files to the destination directory. It does not mutate container stores.

Dependencies and integration points: It reuses the same replication source used by datanode replication paths, making exports faithful to transfer format.

Risks: Destination existence/writability is not prevalidated. If `CONTAINER_NOT_FOUND` occurs after the output file is created, an empty tar path may be left behind.

Test signals: Created tar files, log messages, and successful continuation over missing container IDs.
