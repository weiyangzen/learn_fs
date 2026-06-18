# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/HttpConfig.java

Purpose: `HttpConfig` centralizes Ozone HTTP/HTTPS policy parsing for HDDS web servers.

Important APIs/types/functions: `Policy` has `HTTP_ONLY`, `HTTPS_ONLY`, and `HTTP_AND_HTTPS`, plus `fromString()`, `isHttpEnabled()`, and `isHttpsEnabled()`. `getHttpPolicy(MutableConfigurationSource)` reads `OZONE_HTTP_POLICY_KEY`, validates it, normalizes the config value to the enum name, and returns the policy.

Control flow: Base and component HTTP servers call `getHttpPolicy()` during setup to decide which endpoints to bind. Invalid strings produce `IllegalArgumentException`.

State and persistence: stateless utility class. It mutates the provided configuration by writing the normalized policy name.

Dependencies/integration: depends on Ozone config keys and the mutable configuration abstraction. Used by `BaseHttpServer` and component tests.

Risks: policy parsing is case-insensitive but only accepts exact enum names. Because the method writes back to configuration, callers must expect this normalization side effect.

Test signals: component HTTP server tests and Recon endpoint tests exercise policy combinations; `TestHddsDatanodeService` checks HTTP port behavior for policies.
