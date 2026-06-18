# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/SecurityConfig.java

## Purpose
Central typed view of HDDS/Ozone security configuration. It resolves key algorithms and providers, metadata/key/certificate locations, X.509 durations, block/container token settings, TLS options, external root CA paths, CA rotation settings, certificate polling intervals, and authorization enablement.

## Important APIs and types
Construction reads from `ConfigurationSource` and validates cross-field constraints. `initSecurityProvider` lazily loads the configured provider, dynamically adding Bouncy Castle for `"BC"` when needed. Accessors expose security flags, token flags and expiry, certificate durations, key/certificate paths, key codec creation, TLS provider/protocols/ciphers, external CA paths, CA rotation times/intervals, test-cert mode, and authorization mode.

## Control flow and state
The constructor computes immutable instance fields from config keys. It falls back from HDDS metadata dir to Ozone metadata dirs. Authorization is enabled only when Ozone security or test authorization is enabled and the authorization key is true. TLS test-cert mode is only considered when gRPC TLS is enabled. `validateCertificateValidityConfig` rejects zero/negative durations, default duration greater than max duration, renewal grace greater than default duration, invalid CA rotation intervals/timeouts when rotation is enabled, and block token lifetime exceeding renewal grace when token sanity checks are enabled.

The static security provider field is volatile and initialized under a synchronized method, so provider loading is process-global. `getGrpcTlsProtocols` returns a defensive array copy; cipher list is unmodifiable or null.

## Dependencies and integration points
The class pulls constants from `HddsConfigKeys` and `OzoneConfigKeys`, uses Netty/Ratis `SslProvider`, Java security providers, Bouncy Castle, `KeyCodec`, and `OzoneConsts`. Certificate clients, key storage/generation, token managers, gRPC services, and CA rotation managers depend on it.

## Risks and test signals
Tests should cover invalid duration combinations, CA rotation validation, provider lookup and Bouncy Castle registration, metadata dir fallback, authorization test mode, TLS protocol/cipher parsing, external root CA detection, null metadata directory failures in path getters, and token sanity checks. Since provider initialization is static, tests must isolate or reset provider assumptions carefully.
