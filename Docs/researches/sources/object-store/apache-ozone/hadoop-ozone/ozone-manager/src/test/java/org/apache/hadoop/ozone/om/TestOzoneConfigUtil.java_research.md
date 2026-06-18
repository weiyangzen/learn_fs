# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOzoneConfigUtil.java

Purpose: Tests server-side replication configuration preference resolution.

Important APIs and types: `OzoneConfigUtil.resolveReplicationConfigPreference`, `ReplicationConfig`, `RatisReplicationConfig`, `ECReplicationConfig`, `DefaultReplicationConfig`, `HddsProtos.ReplicationType`, and `HddsProtos.ReplicationFactor`.

Control flow: setup mocks `OzoneManager.getDefaultReplicationConfig` to return RATIS/THREE. Tests call preference resolution with no client preference plus EC bucket default, no bucket default, explicit client EC preference, and RATIS bucket default.

State and persistence: no persistence. State is pure config values and mocked default replication config.

Dependencies and integration points: covers OM key creation config resolution where client, bucket, and server defaults compete.

Risks and edge cases: `ReplicationType.NONE` and `ReplicationFactor.ZERO` mean no client preference; EC proto config must be honored when type is EC; bucket defaults should override server defaults but not explicit client preference.

Test signals: exact object equality to bucket EC config, server RATIS default, client EC config `rs-3-2-1024K`, and RATIS bucket default.
