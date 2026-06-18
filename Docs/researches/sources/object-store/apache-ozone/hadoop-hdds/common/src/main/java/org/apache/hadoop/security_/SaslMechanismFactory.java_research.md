# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/security_/SaslMechanismFactory.java

## Purpose

`SaslMechanismFactory` centralizes the effective SASL mechanism used for Hadoop token/digest authentication in this forked security package.

## APIs and control flow

`getMechanism()` lazily resolves the mechanism from `HADOOP_SASL_MECHANISM` environment variable, then Hadoop configuration key `hadoop.security.sasl.mechanism`, then default `DIGEST-MD5`, caching the result in a volatile field. `getMechanismName(AuthMethod)` returns the configured mechanism for `DIGEST` and `TOKEN`, otherwise the mechanism name built into Hadoop's `AuthMethod`. Helpers identify default and digest mechanisms. `main` prints the effective value.

## State, dependencies, and integration

State is the cached effective mechanism. Dependencies include Hadoop `Configuration`, Hadoop `SaslRpcServer.AuthMethod`, and SLF4J. Both `SaslRpcClient` and `SaslRpcServer` use it when validating advertised auth types and creating clients/servers.

## Risks and test signals

The cached value cannot be refreshed except by classloader reset, so tests that change env/config need isolation. Creating a new `Configuration` ignores service-specific config objects. Tests should cover env precedence, default fallback, TOKEN/DIGEST mapping, non-digest auth method passthrough, and client/server agreement when a custom mechanism is configured.
