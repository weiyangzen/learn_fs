# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFsHAURLs.java

Purpose: tests client-side URI authority parsing and `FsShell` behavior for O3FS/OFS paths in Ozone Manager HA clusters.

Important APIs/types/functions: setup obtains a `MiniOzoneHAClusterImpl`, OM service ID, client, creates a unique volume/bucket, sets `fs.defaultFS` to `o3fs://bucket.volume.serviceId/`, and creates directories. `getLeaderOMNodeAddr`, `getHostFromAddress`, and `getPortFromAddress` derive authority components. Tests cover qualified default FS, unqualified/default-FS variants, and incorrect service IDs for both schemes.

Control flow: `testWithQualifiedDefaultFS` runs `ozone fs -ls` through `FsShell` against `/`, `o3fs:///`, unqualified bucket.volume, leader hostname, leader host:port, service ID, and service ID with port, asserting success or stderr messages. `testOtherDefaultFS` calls `testWithDefaultFS` for file, HDFS, unqualified o3fs, and bucket.volume defaults. `testIncorrectAuthorityInURI` checks correct and dummy service IDs for OFS and O3FS.

State and persistence behavior: creates real volume/bucket and directories in HA OM state, but tests focus on client resolution and shell exit codes. No persistent mutation beyond setup directories is central to assertions.

Dependencies and integration points: uses `HATests.TestCase`, `MiniOzoneHAClusterImpl`, `ConfUtils`, OM address config keys, `FsShell`, `ToolRunner`, O3FS/OFS implementation keys, and Hadoop URI parsing helpers.

Risks: shell stderr text and exit code conventions are part of the assertions. Tests depend on an active OM leader and configuration where `ozone.om.address` can be overridden for leader host/port cases.

Test signals: catches authority parsing regressions, missing service ID validation, incorrect use of ports with service IDs, and bad error reporting for unresolved OM hosts in HA mode.
