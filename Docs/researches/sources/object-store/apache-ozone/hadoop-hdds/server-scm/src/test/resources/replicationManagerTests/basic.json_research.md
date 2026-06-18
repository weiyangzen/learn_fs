# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/resources/replicationManagerTests/basic.json

Purpose: This fixture file provides declarative replication-manager scenarios for basic healthy, under-replicated, and over-replicated containers across Ratis and erasure-coded replication.

Important APIs and types: Each JSON object describes `description`, `containerState`, `replicationConfig`, optional `sequenceId`, `replicas`, optional `pendingReplicas`, `expectation`, optional `checkCommands`, and expected `commands`. Replica entries include state, replica index, datanode alias, sequence ID, empty flag, and origin.

Control flow: The replication-manager test harness reads each object, creates a container state model, injects current and pending replicas, runs the replication check, then compares expected queue counters and command types. This file has scenarios for perfect Ratis and EC replication, Ratis and EC under-replication, pending ADD suppression, Ratis and EC over-replication, pending DELETE suppression, EC simultaneous over/under behavior, and Ratis over-replication already covered by pending delete.

State and persistence behavior: This is fixture data, not runtime persistence. It models SCM's in-memory replication state, pending replica operations, and expected command queues.

Dependencies and integration points: It is consumed by replication-manager parameterized tests and couples to command type names such as `replicateContainerCommand`, `reconstructECContainersCommand`, and `deleteContainerCommand`, plus expectation keys like `underReplicatedQueue` and `overReplicatedQueue`.

Risks: Stringly typed command and counter names must match the harness. The scenarios intentionally simplify datanode identity to aliases, so they depend on deterministic alias expansion by the loader.

Test signals: Expected counters and command lists for ten core Ratis/EC cases, especially suppression of queue commands when pending add/delete operations already exist.
