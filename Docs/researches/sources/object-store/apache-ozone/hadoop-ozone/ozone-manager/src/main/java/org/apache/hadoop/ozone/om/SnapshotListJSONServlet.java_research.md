# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/SnapshotListJSONServlet.java

Purpose: `SnapshotListJSONServlet` exposes a JSON snapshot listing endpoint for a given volume and bucket through the OM HTTP server.

Important APIs and types: It extends `HttpServlet`, loads `OzoneManager` from servlet context, defines a Jackson mix-in to ignore protobuf and transaction-info getters on `SnapshotInfo`, and implements `doGet`.

Control flow: `doGet` validates required `volume` and `bucket` request parameters, reads optional `prefix`, then repeatedly calls `om.listSnapshot(volume, bucket, prefix, lastSnapshot, 1000)` until the response has no next marker. Each page's snapshot info list is serialized to the same writer.

State and persistence behavior: The servlet persists nothing. It streams live snapshot metadata from OM's snapshot listing API.

Dependencies and integration points: It integrates with OM HTTP diagnostics and snapshot metadata management. It depends on `ListSnapshotResponse`, `SnapshotInfo`, and Jackson serialization.

Risks and test signals: Writing each page as a separate JSON array produces concatenated arrays rather than one enclosing JSON document when multiple pages exist. Parameter errors return 400 with text, while all other exceptions return 500. Tests should cover missing parameters, mix-in serialization, paginated output shape, and exceptions from `om.listSnapshot`.
