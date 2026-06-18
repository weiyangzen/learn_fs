# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/resources/replicationManagerTests/quasi_closed.json

Purpose: This large fixture set models quasi-closed Ratis container edge cases for replication-manager tests. It focuses on stuck quasi-closed detection, origin diversity, BCSID differences, open or unhealthy replicas, maintenance/decommission state, and over/under-replication decisions.

Important APIs and types: Scenarios use `containerState` QUASI_CLOSED, `replicationConfig` RATIS:THREE, replica fields `state`, `sequenceId`, `origin`, `operationalState`, and `healthState`, plus expectations such as `quasiClosedStuck`, `quasiClosedStuckUnderReplicated`, `quasiClosedStuckOverReplicated`, `underReplicatedQueue`, `overReplicatedQueue`, and `unhealthy`. Commands include close, replicate, and delete container commands with exact or alternation-style datanode selectors.

Control flow: The test harness iterates each object, materializes replicas from aliases, runs the replication-manager check, verifies metric/queue expectations, and compares generated command types and selected source datanodes. Scenarios cover one open replica needing close, too few quasi-closed replicas needing replication, all origins closed enough to close, unhealthy highest-BCSID handling, correct replication by one/two/three origins, maintenance/decommission suppression, and stale-node restrictions.

State and persistence behavior: Fixture data represents SCM's in-memory replica topology and expected pending work. No durable state is written by the resource itself.

Dependencies and integration points: This file is tightly coupled to Ratis quasi-closed placement logic, origin-based replica health rules, operational state handling, and the replication-manager JSON test loader.

Risks: The fixture is stringly typed and dense; small changes in command selection policy can affect many expected rows. Datanode alternation strings such as `d1|d2` assume the verifier accepts one of several valid choices.

Test signals: Broad signals include stuck quasi-closed counters, under/over queue entries, close commands for open lower-state replicas, replication commands from suitable source replicas, delete commands for over-replicated origins, and no commands when maintenance, decommission, stale, or already-correct origin coverage should suppress action.
