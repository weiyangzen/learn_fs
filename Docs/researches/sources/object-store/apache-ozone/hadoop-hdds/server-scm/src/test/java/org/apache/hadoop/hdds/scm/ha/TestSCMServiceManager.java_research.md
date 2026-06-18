<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMServiceManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMServiceManager.java

Purpose: This suite verifies `SCMServiceManager` propagates SCM context changes to registered services, letting services implement their own leader/safe-mode run conditions.

Important APIs and types: It uses `SCMServiceManager`, `SCMService`, `SCMService.ServiceStatus`, `SCMContext`, and `SafeModeStatus`.

Control flow: Each test creates an inline `SCMService` whose `notifyStatusChanged` sets internal status from a shared `SCMContext`. The first service runs whenever SCM is leader, regardless of safe mode. The second service runs only when SCM is both leader and out of safe mode. The manager registers the service, then context transitions through out-of-safe-mode, leader, in-safe-mode, and step-down states while assertions check `shouldRun`.

State and persistence behavior: State is in-memory service status plus `SCMContext` leader and safe-mode flags. No persistence exists.

Dependencies and integration points: This guards background and HA-aware SCM services that depend on notification fan-out from `SCMServiceManager`.

Risks: Because services decide their own policy, manager regressions would show as missed notification transitions rather than direct policy failure.

Test signals: `shouldRun` toggles exactly according to leader-only and leader-plus-out-of-safe-mode policies.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMServiceManager.java -->
