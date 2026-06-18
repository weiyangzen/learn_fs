# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/security/SecretKeyManagerService.java

Purpose: `SecretKeyManagerService` is the SCM background service that initializes and rotates symmetric secret keys used by secure Ozone components. It runs only when this SCM is the ready leader.

Important APIs and types: The constructor builds `SecretKeyConfig`, `LocalSecretKeyStore`, a Ratis-proxied `SecretKeyState`, and `SecretKeyManager`, then schedules itself. It implements `SCMService` and `Runnable` with `notifyStatusChanged`, `shouldRun`, `run`, `start`, `stop`, `getSecretKeyManager`, and static `isSecretKeyEnable(SecurityConfig)`.

Control flow: `notifyStatusChanged` locks service state. If `SCMContext.isLeaderReady()` is true and the manager is uninitialized, it asynchronously calls `secretKeyManager.checkAndInitialize()`; then it marks service status running. Otherwise it pauses. The scheduled `run` exits unless running, and then calls `checkAndRotate(false)`.

State and persistence behavior: Runtime state is guarded by `serviceLock` and represented by `ServiceStatus`. Secret keys persist through `LocalSecretKeyStore` at the configured SCM CA cert storage directory, while mutations are replicated through the Ratis-backed `SecretKeyState`.

Dependencies and integration points: It integrates SCM leader readiness, SCM Ratis, local secret-key files, `SecretKeyManager`, and security configuration. It is enabled whenever security is enabled.

Risks: The constructor calls `start()`, so instantiation has scheduling side effects. Exceptions in the asynchronous initialization task are rethrown as runtime exceptions inside the executor. The service status is process-local and must be updated on leader transitions to avoid rotating keys on followers.

Test signals: Tests should cover leader-ready initialization, paused follower behavior, scheduled rotation only while running, persisted local key file interaction, Ratis replication of initialized state, and scheduler shutdown.
