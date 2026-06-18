# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/container/ListSubcommand.java

Purpose: `ListSubcommand` prints JSON metadata for every local container replica on the datanode.

Important APIs and types: It uses parent `ContainerCommands`, iterates `parent.getController().getContainers()`, and delegates serialization to `outputContainer`.

Control flow: `call()` loads containers from volumes and writes one pretty JSON object per container.

State and persistence behavior: It reads local container metadata and writes to stdout only.

Dependencies and integration points: It depends fully on `ContainerCommands.loadContainersFromVolumes` to construct the controller view.

Risks: Output is a stream of separate JSON objects rather than a single JSON array, which matters for automation. Large datanodes can produce substantial output.

Test signals: One serialized `ContainerData` object per loaded container.
