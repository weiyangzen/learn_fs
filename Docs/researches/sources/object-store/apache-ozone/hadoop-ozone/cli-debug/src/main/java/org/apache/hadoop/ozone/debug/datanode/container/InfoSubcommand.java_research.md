# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/container/InfoSubcommand.java

Purpose: `InfoSubcommand` prints JSON metadata for one local container replica.

Important APIs and types: It uses parent `ContainerCommands`, `ContainerController.getContainer`, `Container`, and `ContainerCommands.outputContainer`.

Control flow: The command requires `--container`, loads containers from datanode volumes, looks up the container ID in the controller, and pretty-prints `ContainerData` if found.

State and persistence behavior: It reads local datanode container metadata and emits JSON. No writes occur.

Dependencies and integration points: It depends on the parent loading path and container service metadata model.

Risks: Missing containers produce no output and no error, which can be ambiguous for users and automation.

Test signals: JSON output for existing container data and quiet completion for absent IDs.
