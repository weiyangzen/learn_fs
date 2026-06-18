# sources/object-store/apache-ozone/hadoop-hdds/config/src/test/java/org/apache/hadoop/hdds/conf/TestConfigurationSource.java

## Purpose
Tests default methods on `ConfigurationSource` and mutable source interaction with annotated objects.

## Important APIs, Types, And Functions
APIs under test include prefix matching with and without prefix trimming, `getObject`, `reconfigure`, and set-from-object behavior through the mutable implementation.

## Control Flow
The test populates `InMemoryConfigurationForTesting`, checks returned maps, creates `ConfigurationExample`, mutates the backing config, applies reconfiguration, and verifies only the reconfigurable dynamic field changes. It also covers a key whose suffix includes the prefix text.

## State And Persistence
State is in the in-memory map and injected `ConfigurationExample` instances.

## Dependencies And Integration Points
Validates `ConfigurationSource`, `MutableConfigurationSource`, `ConfigurationReflectionUtil`, and `ReconfigurableConfig` integration.

## Risks
Does not cover all typed getters or class loading. The reconfiguration test depends on default injection values remaining stable.

## Test Signals
Signals include prefix map correctness, dynamic-only reconfiguration, and object-to-configuration write-back for prefix-containing names.
