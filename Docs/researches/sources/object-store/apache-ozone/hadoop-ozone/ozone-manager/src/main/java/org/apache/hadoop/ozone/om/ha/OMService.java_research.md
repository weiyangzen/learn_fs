# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ha/OMService.java

Purpose: `OMService` defines a lifecycle and status-notification contract for stateful OM background services that react to HA or safe-mode state changes.

Important APIs and types: Methods include `notifyStatusChanged`, `shouldRun`, `getServiceName`, `start`, and `stop`. `ServiceStatus` currently contains `RUNNING` and `PAUSING`.

Control flow: The interface defines no implementation. `OMServiceManager` calls these methods on registered services.

State and persistence behavior: Implementations decide their own runtime state and persistence. The interface carries no state.

Dependencies and integration points: OM background services can implement this to pause/resume based on leadership, Ratis readiness, or safe mode.

Risks and test signals: Implementations need clear semantics for `shouldRun` around leadership transitions. Tests should cover manager notification, start failure handling, stop idempotence, and paused service behavior.
