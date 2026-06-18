# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMService.java

Purpose: Common lifecycle and status-notification interface for SCM background services such as replication, block deletion, pipeline creation, and HA transaction monitoring.

Important APIs and types: Methods include `notifyStatusChanged`, optional `notifyEventTriggered`, `shouldRun`, `getServiceName`, `start`, and `stop`. Nested enums define `ServiceStatus` and one-time `Event` values.

Control flow: `SCMServiceManager` calls notification methods when safe mode, leader status, or other SCM events change. Service implementations use `shouldRun` to decide whether a scheduled iteration should execute.

State and persistence behavior: No persistence in the interface. Implementations may own runtime state and, for `StatefulService`, durable configuration.

Dependencies and integration points: Used throughout SCM service registration and status propagation. It is also the base for `StatefulService`.

Risks and test signals: Event handling is optional by default, so missing overrides can silently ignore new events. Tests should assert service managers notify all registered services, start errors are handled, and `shouldRun` semantics match leader/safe-mode transitions.
