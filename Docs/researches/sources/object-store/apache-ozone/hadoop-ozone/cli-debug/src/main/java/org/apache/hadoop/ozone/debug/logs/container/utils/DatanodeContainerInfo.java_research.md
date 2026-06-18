# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/utils/DatanodeContainerInfo.java

Purpose: `DatanodeContainerInfo` is an immutable value object representing one parsed container log event for a datanode.

Important APIs and types: It exposes a nested `Builder` with setters for container ID, datanode ID, timestamp, state, BCSID, error message, log level, and index value, plus getters for all fields.

Control flow: Construction is builder-only. The builder stores mutable interim values, and `build` copies them into final fields without validation.

State and persistence behavior: The object is in-memory only but directly maps to columns in `DatanodeContainerLogTable`. Default primitive values are zero if parser code does not set them; strings can remain null.

Dependencies and integration points: It is produced by `ContainerLogFileParser`, consumed by `ContainerDatanodeDatabase`, and re-created from SQL query results for health analysis.

Risks: Lack of validation means partially parsed events can become database rows. There is no equals/hashCode/toString, so debugging and collection comparisons need custom field checks.

Test signals: Builder round-trip tests should verify all fields, default unset values, and database insert/query compatibility.
