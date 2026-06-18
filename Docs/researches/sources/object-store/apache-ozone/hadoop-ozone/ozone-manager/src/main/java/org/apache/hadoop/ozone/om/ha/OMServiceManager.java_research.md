# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ha/OMServiceManager.java

Purpose: `OMServiceManager` registers and coordinates OM background services implementing `OMService`.

Important APIs and types: Public synchronized methods are `register`, `notifyStatusChanged`, `start`, and `stop`. It stores services in an `ArrayList`.

Control flow: `register` rejects null and appends the service. `notifyStatusChanged` iterates and calls each service. `start` iterates all services, catching and logging `OMServiceException` so one service failure does not block the rest. `stop` iterates and calls `stop` without exception handling.

State and persistence behavior: State is in-memory service registration order. No durable data is written.

Dependencies and integration points: OM startup and shutdown code use it to coordinate services that depend on HA readiness or safe mode state.

Risks and test signals: All methods synchronize on the manager, so a slow service callback blocks registration and other lifecycle operations. `stop` does not isolate runtime exceptions. Tests should cover registration order, null rejection, start continuation after checked failure, status notifications, stop ordering, and behavior when a service throws unchecked exceptions.
