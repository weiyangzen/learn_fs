# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/security/ScmSecretKeyStateBuilder.java

Purpose: This builder creates a `SecretKeyState` implementation wrapped in an SCM Ratis proxy so secret-key state mutations annotated for replication are applied through the HA state machine.

Important APIs and types: Setters accept a `SecretKeyStore` and `SCMRatisServer`. `build()` constructs `SecretKeyStateImpl(secretKeyStore)` and wraps it with `scmRatisServer.getProxyHandler(new SecretKeyStateInvoker(...))`.

Control flow: There is no branching. The builder defers all behavior to `SecretKeyStateImpl`, `SecretKeyStateInvoker`, and Ratis proxy infrastructure.

State and persistence behavior: This class owns no persistent state. The supplied `SecretKeyStore` controls local secret-key storage, while Ratis replication controls distributed state ordering.

Dependencies and integration points: It is used by `SecretKeyManagerService` to build the state object consumed by `SecretKeyManager`. It depends on SCM HA being present and usable.

Risks: There are no null checks. A missing store or Ratis server will fail at build time with a null-pointer style error. The class assumes all secret-key state mutations must go through the proxy; bypassing it would skip replication.

Test signals: Tests should verify that a built state object routes mutating calls through `SecretKeyStateInvoker` and that missing dependencies fail clearly.
