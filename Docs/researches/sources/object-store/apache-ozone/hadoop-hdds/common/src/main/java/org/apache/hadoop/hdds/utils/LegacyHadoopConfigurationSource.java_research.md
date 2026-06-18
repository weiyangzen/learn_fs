# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/LegacyHadoopConfigurationSource.java

## Purpose
Adapts a Hadoop `Configuration` to Ozone's `MutableConfigurationSource` while preserving access to the original Hadoop configuration for legacy Hadoop APIs.

## Important APIs, Types, And Functions
`LegacyHadoopConfigurationSource` wraps a defensive `Configuration` copy whose `getProps()` returns `DelegatingProperties` with crypto-compliance filtering. Public APIs are `get`, `getPassword`, `getConfigKeys`, `set`, `asHadoopConfiguration`, and `getOriginalHadoopConfiguration`.

## Control Flow
Construction creates an anonymous `Configuration` subclass. On first `getProps()`, it reads the compliance mode without filtering, gathers properties tagged `CRYPTO_COMPLIANCE`, and builds `DelegatingProperties`; `reloadConfiguration()` clears that cache. `iterator()` delegates to the filtered properties. `asHadoopConfiguration()` accepts either a real `Configuration` or this wrapper, and rejects other `ConfigurationSource` implementations.

## State And Persistence
State is the wrapped `Configuration` plus cached `delegatingProps` inside the anonymous subclass. `set()` mutates the wrapped Hadoop configuration in memory; persistence is whatever Hadoop `Configuration` resources provide.

## Dependencies And Integration Points
Integrates `org.apache.hadoop.conf.Configuration`, Ozone `ConfigurationSource`, `MutableConfigurationSource`, `DelegatingProperties`, `ConfigTag`, and `OzoneConfigKeys`. It intentionally catches `NoSuchMethodError` so Hadoop 2 runtimes without `getAllPropertiesByTag` still work.

## Risks
The wrapper makes a new `Configuration(configuration)`, so clients expecting shared object identity can be surprised. Crypto compliance depends on Hadoop property tagging availability. `getConfigKeys()` calls `getPropsWithPrefix("")`, which may force property materialization. `asHadoopConfiguration()` is server-side oriented and throws on non-Hadoop Ozone configs.

## Test Signals
`TestOzoneConfiguration` covers wrapping and `asHadoopConfiguration`. Useful extra tests are crypto-compliance filtering, Hadoop 2 compatibility behavior, reload invalidation, password-provider access, and mutation visibility through `set()`.
