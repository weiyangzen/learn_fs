# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyConfig.java

## Purpose
`SecretKeyConfig` resolves configuration for symmetric secret-key lifecycle management: local file path, rotation duration, expiry duration, HMAC algorithm, and rotation check interval.

## Important APIs, Types, And Functions
The constructor builds `localSecretKeyFile` from metadata dir, component name, key dir, and file name config keys. Static parsers `parseExpiryDuration()`, `parseRotateDuration()`, and `parseRotateCheckDuration()` read configured durations in milliseconds. Getters expose resolved values.

## Control Flow
Construction reads config keys with defaults and converts durations to `Duration`. It first tries `HDDS_METADATA_DIR_NAME`, falling back to `OZONE_METADATA_DIRS`.

## State, Persistence, And Dependencies
State is immutable resolved config. Persistence is external through the local file path consumed by `LocalSecretKeyStore`. Dependencies are HDDS config constants, `ConfigurationSource`, paths, durations, and time units.

## Integration Points
`SecretKeyManager`, `DefaultSecretKeySignerClient`, and `DefaultSecretKeyVerifierClient` all use these parsed values to manage key generation, polling, caching, and storage.

## Risks
Missing metadata directory can produce an invalid path or null handling issue depending on `Paths.get(...)`. Invalid zero/negative durations can break rotation or cache math because this class does not validate them.

## Test Signals
Tests should cover default resolution, metadata fallback, component-specific path building, duration parsing, algorithm selection, and invalid/missing config handling.
