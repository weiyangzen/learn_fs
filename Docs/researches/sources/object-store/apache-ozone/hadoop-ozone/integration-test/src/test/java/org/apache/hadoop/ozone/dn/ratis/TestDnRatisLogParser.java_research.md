# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/ratis/TestDnRatisLogParser.java

Purpose: Integration test for parsing datanode Ratis log segment files with the debug `RatisLogParser`.

Important APIs, types, and functions: Uses `MiniOzoneCluster`, `OzoneConfiguration`, `OZONE_SCM_RATIS_PIPELINE_LIMIT`, `HDDS_CONTAINER_RATIS_DATANODE_STORAGE_DIR`, and `RatisLogParser.parseRatisLogs` with `smToContainerLogString`.

Control flow: Setup builds a one-datanode mini cluster, redirects `System.out` and `System.err` to byte-array streams, and waits for readiness. The test locates the first SCM pipeline ID, derives the datanode Ratis pipeline `current/log_inprogress_0` file, waits for its existence, invokes the parser, and asserts stdout contains total entry statistics.

State and persistence behavior: The mini cluster persists Ratis logs under the datanode Ratis storage directory. The parser reads the in-progress segment file and emits text to stdout. The test mutates global process stdout/stderr and closes the capture streams during cleanup.

Dependencies and integration points: Bridges live datanode Ratis storage layout with the debug log parser. It depends on pipeline creation and Ratis log file naming.

Risks: Redirecting global stdout/stderr can affect parallel tests. In-progress log file creation is timing-sensitive. Ratis storage layout or segment naming changes would break path derivation.

Test signals: The log segment file must exist and be a file; parser output must contain `Num Total Entries:`.
