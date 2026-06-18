# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/resources/replicationManagerTests/mismatched_replicas.json

Purpose: This fixture covers a closed Ratis container whose replicas are in mismatched states, specifically open replicas alongside a closed replica.

Important APIs and types: The scenario uses `containerState` CLOSED, `replicationConfig` RATIS:THREE, three replicas with states OPEN, OPEN, and CLOSED, and `checkCommands` expecting close-container commands for the open replica datanodes.

Control flow: The replication-manager harness loads the fixture, builds the replica set, runs the container check, and verifies that the manager schedules close commands to bring mismatched open replicas toward the container's closed state rather than enqueueing over-replication work.

State and persistence behavior: The file is static fixture data. It represents SCM's in-memory view of replica lifecycle state and expected command emission.

Dependencies and integration points: It depends on the shared replication-manager JSON schema and command verifier recognizing `closeContainerCommand` and datanode aliases `d1` and `d2`.

Risks: The file lacks a trailing newline between JSON arrays in some concatenated terminal views, but the actual file is a valid JSON array. Because it is a single scenario, it does not cover EC mismatch or quasi-closed mismatch behavior.

Test signals: No over-replicated queue work and two close-container check commands targeting the open replicas.
