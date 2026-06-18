# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ha/TestOMServiceManager.java

Purpose: Tests `OMServiceManager` notification flow for services that should run only when OM is leader.

Important APIs and types: `OMServiceManager`, `OMService`, `ServiceStatus`, and `OMServiceException`.

Control flow: the test defines a small context with a mutable leader boolean and an anonymous `OMService` whose `notifyStatusChanged` sets status to RUNNING or PAUSING from that boolean. It registers the service, toggles leader state, calls `notifyStatusChanged`, and checks `shouldRun`.

State and persistence: all state is in-memory service status. No persistence.

Dependencies and integration points: OM background services use this manager to react to HA role transitions.

Risks and edge cases: services must begin paused, transition to running on leadership, and pause again after step-down. Missing notification would leave services running on followers.

Test signals: `shouldRun` is false initially, true after becoming leader, and false after stepping down.
