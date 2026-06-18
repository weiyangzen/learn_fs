## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/StandaloneReplicationConfig.java

Purpose: immutable replication config for legacy STANDALONE replication.

Important APIs: cached `getInstance` for ONE/THREE, factor/type/required-node getters, JSON `replicationType()` returning `"STANDALONE"` while `getReplicationType()` returns proto `STAND_ALONE`, string/config format, equality/hash, and minimum nodes equal to factor.

Control flow/state: final factor with singleton common instances. Dependencies: Jackson, HDDS protobufs, JCIP immutable.

Integration points: legacy replication paths, `ReplicationConfig` factories, JSON output that expects `STANDALONE` spelling, default replication proto. Risks: dual spelling (`STAND_ALONE` vs `STANDALONE`) is compatibility-sensitive; `getMinimumNodes` differs from RATIS by requiring all replicas. Test signals: JSON spelling, singleton behavior, config format matching validator, equality/hash, and proto legacy round trips.
