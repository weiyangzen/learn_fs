# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/container/ContainerCommands.java

Purpose: `ContainerCommands` groups datanode-local container replica debug commands and builds a read-only container view from configured storage volumes.

Important APIs and types: It extends `AbstractSubcommand`, uses `OzoneConfiguration`, `MutableVolumeSet`, `ContainerSet`, `ContainerController`, `ContainerReader`, `Handler`, `HddsVolume`, `DatanodeVersionFile`, `StorageVolumeUtil`, `HddsVolumeUtil`, `ContainerChecksumTreeManager`, and `JsonUtils`.

Control flow: `loadContainersFromVolumes` validates configured storage directories, creates a read-only `ContainerSet`, reads datanode UUID and cluster ID from storage metadata, creates volume sets and handlers, optionally loads schema-v3 DB stores read-only, then runs `ContainerReader` over each HDDS volume. Subcommands consume `getController()` and `getVolumeSet()`.

State and persistence behavior: It reads datanode VERSION files, storage directories, container metadata, and possibly RocksDB stores. Runtime state is the loaded `volumeSet` and `controller`; no mutation is intended.

Dependencies and integration points: It is the parent for list/info/export/inspect and reuses datanode container service internals outside a running datanode.

Risks: It assumes at least one configured storage directory and at least one cluster ID directory under `hdds`. Missing directories produce `IOException`; `findFirst().get()` can throw if no cluster dir exists.

Test signals: Successful container loading, JSON output from `outputContainer`, and clear errors for missing storage directories.
