# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/VersionDebug.java

Purpose: `VersionDebug` prints local Ozone component version metadata as JSON without contacting services.

Important APIs and types: It implements `Callable<Void>` and `DebugSubcommand`, registers with `@MetaInfServices`, uses `ClientVersion`, `DatanodeVersion`, `OzoneManagerVersion`, `ComponentVersion`, `OzoneVersionInfo`, Guava `ImmutableSortedMap`, and `JsonUtils`.

Control flow: `call()` constructs a sorted nested map containing Ozone revision/url/version plus current component version names and protobuf values, then pretty-prints it to stdout.

State and persistence behavior: No state is modified or persisted. Output reflects constants in the loaded artifacts.

Dependencies and integration points: The command helps compare feature support across nodes and integrates into the debug CLI command registry.

Risks: It reports only the local classpath/artifact versions, not live cluster versions. If a component enum changes, `asMap` still serializes only the current constant.

Test signals: Valid JSON with `ozone` and `components` keys, and component version entries for client, datanode, and OM.
