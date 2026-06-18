# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/ReadOnlyHealthyToHealthyNodeHandler.java

Purpose: `ReadOnlyHealthyToHealthyNodeHandler` handles transitions from `HEALTHY_READONLY` back to `HEALTHY`, typically after a datanode has finalized and its layout versions match SCM again.

Important APIs and types: It implements `EventHandler<DatanodeDetails>` and depends on `SCMServiceManager` plus `SCMService.Event.UNHEALTHY_TO_HEALTHY_NODE_HANDLER_TRIGGERED`.

Control flow: On event, it logs the transition and notifies the service manager that the healthy transition handler has fired. It does not mutate node, pipeline, or container state directly.

State and persistence behavior: The handler has no mutable state beyond its service-manager reference. State transitions have already been applied by `NodeStateManager` before the event is handled.

Dependencies and integration points: It connects upgrade/layout health recovery to SCM service lifecycle notifications. Services waiting for healthy-node transitions can use the notification to re-evaluate readiness or resume work.

Risks: The event name says "UNHEALTHY_TO_HEALTHY" even though the specific transition is readonly-to-healthy, so consumers must understand the broader service event semantics. No exception handling is present around service notification.

Test signals: Tests should verify that the service event is emitted exactly once per handler invocation and that no other managers are touched.
