# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/ContainerInfoCommand.java

Purpose: `ContainerInfoCommand` prints state-transition history and analysis for one container from the parsed container-log SQLite database.

Important APIs and types: It extends `AbstractSubcommand`, uses a positional `Long containerId`, parent `ContainerLogController`, and `ContainerDatanodeDatabase.showContainerDetails`.

Control flow: The command rejects negative IDs with stderr output, resolves the DB path through the parent, constructs `ContainerDatanodeDatabase`, and delegates display/analysis to `showContainerDetails`.

State and persistence behavior: It reads the SQLite database created by the parse command. It does not write state.

Dependencies and integration points: It is a query command over the container log database utility package.

Risks: A negative ID returns normally rather than failing the command. Most behavior is delegated to utility classes outside this work item.

Test signals: Error for negative ID and detailed per-container output for valid IDs in the DB.
