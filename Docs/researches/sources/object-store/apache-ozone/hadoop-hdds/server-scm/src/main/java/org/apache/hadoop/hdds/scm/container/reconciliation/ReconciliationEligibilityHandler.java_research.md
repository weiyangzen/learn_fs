# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/reconciliation/ReconciliationEligibilityHandler.java

Purpose: utility that decides whether a container may be reconciled.

Important APIs: static `isEligibleForReconciliation`, eligible container/replica state sets, enum `Result`, and nested `EligibilityResult`.

Control flow and state: fetches container and replicas from `ContainerManager`; rejects missing containers, non-CLOSED/non-QUASI_CLOSED containers, empty replicas, replica states outside CLOSED/QUASI_CLOSED/UNHEALTHY, non-Ratis replication, and replication configs with required nodes <= 1. Returns `OK` otherwise.

Dependencies and integration: called by `ReconcileContainerEventHandler` and tested in `TestReconcileContainerEventHandler`.

Risks: OK message concatenates instead of formatting (`"Container %s..." + containerID`), so it contains a literal `%s`. Eligibility ignores datanode operational/health state until HDDS-10714. Test signals should assert every rejection reason and message, plus eligible CLOSED and QUASI_CLOSED Ratis containers.
