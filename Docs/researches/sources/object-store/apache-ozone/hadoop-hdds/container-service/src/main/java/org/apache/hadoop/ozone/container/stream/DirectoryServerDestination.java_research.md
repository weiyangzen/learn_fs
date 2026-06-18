# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/DirectoryServerDestination.java

Purpose: maps streamed logical file names into a single destination root directory.

Important APIs and functions: the constructor stores the root `Path`. `mapToDestination(String name)` resolves the provided name as a path below that root.

Control flow and state: there is no validation or normalization beyond `Path.resolve(Paths.get(name))`. The root field is instance state and not mutated after construction in normal use.

Dependencies and integration: used by `DirstreamClientHandler` through the `StreamingDestination` interface.

Risks and test signals: logical names containing absolute paths or `..` may escape the intended destination depending on platform path semantics. Tests should cover nested names, root resolution, absolute-name handling, and whether callers sanitize server-provided logical names.
