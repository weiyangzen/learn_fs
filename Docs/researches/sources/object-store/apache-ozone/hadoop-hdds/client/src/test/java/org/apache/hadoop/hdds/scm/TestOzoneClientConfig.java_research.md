## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/TestOzoneClientConfig.java

**Purpose:** Tests binding of `OzoneClientConfig` from `OzoneConfiguration`, including size parsing, HBase enhancement gating, write concurrency defaults, and stream-read options.

**Important APIs/types/functions:** `missingSizeSuffix()` sets `ozone.client.bytes.per.checksum` as a raw integer and verifies the config falls back to `OZONE_CLIENT_BYTES_PER_CHECKSUM_MIN_SIZE`. `testClientHBaseEnhancementsAllowedTrue()` and `testClientHBaseEnhancementsAllowedFalse()` show that `ozone.client.hbase.enhancements.allowed` gates incremental chunk lists, putblock piggybacking, and max concurrent writes. `testStreamReadConfigParsing()` validates numeric byte values and a duration string for stream read pre-read size, response size, and timeout.

**Control flow:** Each test creates a fresh `OzoneConfiguration`, sets keys, calls `conf.getObject(OzoneClientConfig.class)`, and asserts the post-processed object values. The HBase tests exercise the conditional normalization branch where related options are honored or reset.

**State and persistence:** Configuration is transient and in-memory. The behavior affects persisted runtime settings only when a site config supplies these keys.

**Dependencies and integration points:** Depends on HDDS config reflection/annotation processing, `OzoneConfigKeys`, `Duration`, and JUnit. Integrates with client write and read stream code that consumes `OzoneClientConfig`.

**Risks:** Silent fallback for a missing size suffix can hide operator mistakes; this test documents current compatibility behavior. Gated HBase enhancements create coupling between one master flag and several feature-specific settings.

**Test signals:** Good coverage for config parsing and post-processing. It does not test every annotated `OzoneClientConfig` field or invalid duration/size formats beyond the checksum suffix case.
