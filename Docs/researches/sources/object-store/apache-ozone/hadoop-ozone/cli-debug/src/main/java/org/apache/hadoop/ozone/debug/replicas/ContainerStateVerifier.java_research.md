# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/ContainerStateVerifier.java

Purpose: `ContainerStateVerifier` implements the `containerState` replica verification check, combining datanode-reported container state, SCM container state, and SCM replica-count health.

Important APIs and types: It implements `ReplicaVerifier`, uses `ContainerOperationClient`, `XceiverClientManager`, Guava `Cache<Long, ContainerInformation>`, `ContainerProtocolCalls.readContainer`, `ContainerInfo`, `ContainerReplicaInfo`, `ContainerHealthResult`, and `BlockVerificationResult`.

Control flow: For each block replica, it fetches container information from SCM or cache, reads container data from the target datanode using the encoded token, compares replica state and SCM lifecycle state against allowed sets, computes a replication status from SCM replica information, and passes only when replication is healthy and both states are acceptable.

State and persistence behavior: The verifier is read-only. Runtime state is a bounded container info cache, including SCM lifecycle state, encoded token, and computed replication status. Invalid cache size falls back to one million entries with a stderr warning.

Dependencies and integration points: It is selected by `ReplicasVerify --container-state`, shares SCM/datanode clients with other replica checks, and reports container-level replication problems on every replica output for that container.

Risks: Replica-count health is simplified to non-`UNHEALTHY` string comparisons and required-node count; it may not reflect full SCM placement policy. Cache entries can become stale during a long-running command. `IOException` message matching for missing containers is string-based.

Test signals: Tests should cover good states, bad replica states, bad SCM states, missing container data, missing container exception classification, cache hit/miss, invalid cache size fallback, under/over replication text, and SCM replica fetch failure.
