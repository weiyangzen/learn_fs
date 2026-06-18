## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/ReplicationSupervisorSchedulingBenchmark.java

Purpose: Manual scheduling-efficiency benchmark for `ReplicationSupervisor`; it is intentionally not named as a normal `Test*` class but contains a JUnit method for ad hoc validation.

Important APIs/types/functions: `ReplicationSupervisor.newBuilder`, `ReplicationTask`, `ReplicateContainerCommand.fromSources`, `ContainerReplicator`, `MockDatanodeDetails`, `Time.monotonicNow`, and resource-lock maps.

Control flow: Builds two source datanodes, per-datanode volume locks, and local destination locks. A synthetic replicator randomly locks a remote volume for download and a local disk for import, waiting one second each. The benchmark schedules 100 tasks and asserts total runtime under 100 seconds.

State and persistence behavior: No real container persistence; only synchronized lock objects and console output simulate constrained disks.

Dependencies and integration points: Models interaction between supervisor scheduling and remote/local disk contention.

Risks and test signals: Uses `Object.wait(1000)` without notifications as a sleep mechanism and random source/disk selection, so timing can be noisy. Useful for manual regression checks, not deterministic CI signal.
