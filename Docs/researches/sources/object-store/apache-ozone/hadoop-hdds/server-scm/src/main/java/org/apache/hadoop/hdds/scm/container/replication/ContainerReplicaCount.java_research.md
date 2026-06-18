# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ContainerReplicaCount.java

Purpose: common interface for Ratis and EC replica-count health calculations.

Important APIs: container/replica getters, sufficient/over-replicated checks, offline safety check, decommission/maintenance counts, `isHealthy`, `isHealthyEnoughForOffline`, and `isUnrecoverable`.

Control flow and state: default `isHealthy()` requires container lifecycle CLOSED or QUASI_CLOSED and all IN_SERVICE replicas to compare equal to the container state via `ReplicationManager.compareState`.

Dependencies and integration: implemented by Ratis and EC replica-count classes, used by ReplicationManager and datanode admin/decommission workflows. Tests exercise concrete implementations and admin monitor decisions.

Risks: default health ignores replicas not in persisted IN_SERVICE state; correctness depends on `DatanodeDetails.getPersistedOpState()` freshness. Test signals should cover maintenance/decommission states, quasi-closed comparison rules, and offline eligibility.
