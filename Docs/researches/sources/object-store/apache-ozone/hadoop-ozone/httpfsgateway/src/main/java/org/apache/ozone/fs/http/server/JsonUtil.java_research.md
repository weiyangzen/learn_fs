# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/fs/http/server/JsonUtil.java

## Purpose
`JsonUtil` provides package-local JSON serialization helpers for HttpFS responses that are easier to express with Jackson than json-simple maps.

## Important APIs, Types, and Functions
The class has a shared static `ObjectMapper`. Public helpers serialize a key/value pair, an arbitrary object, `FsServerDefaults`, and `SnapshotDiffReport`. Private `toJsonMap()` methods convert `FsServerDefaults` and snapshot diff entries into stable map structures.

## Control Flow
Callers pass an object or domain type, `JsonUtil` builds a map when necessary, and Jackson writes JSON. `toJsonString(String,Object)` catches `IOException` and returns null, while other serialization methods declare or avoid checked exceptions depending on path.

## State and Persistence Behavior
No persistent state. The shared mapper is process-global and reused for performance.

## Dependencies and Integration Points
It is used by `HttpFSServer`, `FSOperations`, `CheckUploadContentTypeFilter`, and exception/error paths to serialize redirects, snapshot diffs, server defaults, and simple error maps. It depends on Jackson, HDFS `DFSUtilClient`, `FsServerDefaults`, and `SnapshotDiffReport`.

## Risks and Edge Cases
Returning null on serialization failure can produce weak error behavior. The shared mapper is safe as long as it is not reconfigured after initialization, which the code comments acknowledge. Snapshot and defaults JSON shapes must match WebHDFS client expectations.

## Test Signals
No direct test in this subset. Serialization compatibility should be tested against expected WebHDFS JSON fixtures.
