# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestOpenKeyCleanupService.java

Purpose: Tests `OpenKeyCleanupService` expiration behavior for ordinary open keys, hsync lease recovery, recovery-in-progress hsync keys, and multipart-upload open part keys across default and FSO layouts. Important APIs and types include `OpenKeyCleanupService`, `ExpiredOpenKeys`, `OMMetrics`, `OzoneManagerProtocol`, `OpenKeySession`, `OmMultipartInfo`, `BucketLayout`, lease config keys, and mocked SCM container pipeline lookup.

Control flow: Setup enables HBase enhancements and hsync with very short hard lease and cleanup thresholds. Parameterized tests create open keys, wait for expiration, verify expired-key discovery, resume cleanup, and wait for table cleanup/counter increments. Hsync tests mock an open pipeline, ensure expired recoverable hsync keys are auto-committed, ensure keys with recovery flag remain open, and verify directory path file names. MPU tests ensure committed MPU open keys are excluded, while uncommitted MPU part keys are cleaned.

State and persistence behavior: The suite manipulates open key tables, key tables, multipart tables, metrics counters, lease recovery flags, and allocated block metadata. Dependencies include OM lease semantics, hsync commit path, bucket layout table selection, MPU metadata distinction, and SCM container client.

Risks: Ordered tests share one OM instance and use sleep-based expiration. Test signals are expired-key counts, open/key table emptiness or retained recovery keys, submitted-open-key count, hsync/open cleanup metrics, and preserved MPU parent keys.
