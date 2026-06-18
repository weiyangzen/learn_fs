## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/SetReplicationConfigHandler.java

Purpose: bucket command for setting the default replication config on an existing bucket.

Important APIs and control flow: mixes in optional shell replication options, but `execute` requires explicit replication parameters by calling `replication.fromParams(getConf()).orElseThrow`. It resolves the target bucket and calls `bucket.setReplicationConfig(replicationConfig)`.

State and dependencies: persists bucket default replication metadata through OM. Depends on `ShellReplicationOptions`, `ReplicationConfig`, `OzoneIllegalArgumentException`, and Ozone bucket APIs.

Risks and test signals: rejects config fallback to avoid accidental changes from defaults; users must supply type/config explicitly. No direct tests in this subset.
