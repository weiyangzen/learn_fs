# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/MutableConfigurationSource.java

## Purpose
Combines read-only and write-only configuration contracts for mutable configuration providers.

## Important APIs, Types, And Functions
Extends `ConfigurationSource` and `ConfigurationTarget` without adding methods.

## Control Flow
Implementations can both provide source values for object injection and accept write-back from config POJOs via `setFromObject` on concrete classes or `ConfigurationReflectionUtil.updateConfiguration`.

## State And Persistence
All state is implementation-owned; the interface itself has no fields.

## Dependencies And Integration Points
Used by test in-memory configuration and production mutable configuration classes such as Ozone configuration wrappers.

## Risks
Because no additional contract is enforced, implementers must keep read and write views consistent and handle null/password behavior explicitly.

## Test Signals
Signals include round-trip tests that inject an object from a mutable source, mutate object fields, write back, and read the same keys.
