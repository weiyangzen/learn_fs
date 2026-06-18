# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestSnapshotListJSONServlet.java

Purpose: Tests Jackson serialization for snapshot-list servlet output using `SnapshotListJSONServlet.SnapshotInfoMixin`.

Important APIs and types: `SnapshotListJSONServlet.SnapshotInfoMixin`, `SnapshotInfo`, Jackson `ObjectMapper`, `SnapshotInfo.newInstance`, and `Time.now`.

Control flow: the test registers the mixin on an object mapper, creates one snapshot info object, serializes a singleton list, and checks that problematic internal fields are excluded while the snapshot name is included.

State and persistence: no persistence; serialization happens in memory.

Dependencies and integration points: protects JSON servlet output from leaking protobuf or transaction internals that are not intended for HTTP clients and may be hard to serialize.

Risks and edge cases: changes to `SnapshotInfo` fields or mixin annotations can reintroduce unwanted fields or omit expected public fields.

Test signals: serialization does not throw, JSON lacks `protobuf`, `createTransactionInfo`, and `lastTransactionInfo`, and includes `"name":"snap1"`.
