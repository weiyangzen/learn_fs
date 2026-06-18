# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFileSystemWithStreamingDisabledDatanode.java

Purpose: verifies client-side datastream writes fail fast when datanode-side RATIS datastream ports are disabled, instead of silently falling back to the old gRPC/HTTP2 path.

Important APIs/types/functions: setup disables `HDDS_CONTAINER_RATIS_DATASTREAM_ENABLED`, enables `OZONE_FS_DATASTREAM_ENABLED`, sets auto-threshold to 1 byte, and creates a three-DN FSO O3FS bucket. `testDatastreamWriteFailsFastWhenDatanodeStreamingDisabled` writes a 3 MiB file and expects `IOException`. `collectMessages` flattens the exception cause chain.

Control flow: set O3FS default URI, create random bytes above threshold, attempt create/write/close, then inspect the exception messages for datastream-port validation text and absence of HTTP/2 or timeout fallback indicators.

State and persistence behavior: the write is expected to fail; no successful file content persistence is asserted. The important state is pipeline metadata missing `RATIS_DATASTREAM` ports.

Dependencies and integration points: uses datastream configuration, `MiniOzoneCluster`, O3FS, and client write path validation.

Risks: assertion matches a set of allowed message fragments rather than a specific exception type. If lower layers change wording, test may need updates while preserving fail-fast semantics.

Test signals: detects regressions where the client proceeds with datastream despite missing datanode support or degrades into slow gRPC/HTTP2 timeout failures.
