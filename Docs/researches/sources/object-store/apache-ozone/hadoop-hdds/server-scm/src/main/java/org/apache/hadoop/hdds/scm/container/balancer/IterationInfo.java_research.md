# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/IterationInfo.java

Purpose: immutable metadata for a Container Balancer iteration: number, result text, and duration.

Important APIs: constructor and getters for `Integer iterationNumber`, `String iterationResult`, and `Long iterationDuration`.

Control flow and state: construction boxes the primitive duration into `Long`; no validation, persistence, or mutation after construction.

Dependencies and integration: included in `ContainerBalancerTaskIterationStatusInfo` and surfaced in current/history balancer status tests.

Risks: nullable result is tolerated by proto conversion in the aggregate, but nullable iteration number or duration would fail later. Test signals should cover successful and failed iteration result reporting, including in-progress or not-yet-set result text if used by callers.
