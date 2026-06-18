# sources/object-store/apache-ozone/hadoop-hdds/config/src/test/java/org/apache/hadoop/hdds/conf/InMemoryConfigurationForTesting.java

## Purpose
Simple mutable map-backed configuration source used by unit tests.

## Important APIs, Types, And Functions
Implements `MutableConfigurationSource` with `get`, `getConfigKeys`, `getPassword`, and `set`. Constructors create an empty map or one initial key/value.

## Control Flow
Tests set raw strings, then use default interface methods for typed reads, object injection, prefix scans, and write-back. Password reads return the stored string as a char array.

## State And Persistence
State is a `HashMap<String,String>` owned by the test instance; it is not synchronized or persisted.

## Dependencies And Integration Points
Used by config unit tests and examples. Relies heavily on default methods from `ConfigurationSource` and `ConfigurationTarget`.

## Risks
`getPassword` will throw `NullPointerException` for missing keys. The map is mutable and unsynchronized, so it is not suitable for concurrent tests without wrapping.

## Test Signals
Signals include prefix matching, typed setter/getter round trips, object injection from defaults and overrides, and password behavior for present keys.
