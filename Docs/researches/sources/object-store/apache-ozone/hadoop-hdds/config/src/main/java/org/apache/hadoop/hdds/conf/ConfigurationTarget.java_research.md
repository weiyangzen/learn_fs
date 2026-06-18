# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigurationTarget.java

## Purpose
Write abstraction for configuration stores with typed default setters.

## Important APIs, Types, And Functions
Requires `set(String, String)`. Defaults write ints, longs, doubles, floats, booleans, time durations, storage sizes, string arrays, classes, and enums as strings.

## Control Flow
Reflection write-back calls `ConfigType.set`, which delegates to these typed setters. Time duration and storage setters preserve the annotation's unit in string form through utility formatting.

## State And Persistence
State is persisted only by implementers; this interface just normalizes conversion to string values.

## Dependencies And Integration Points
Used by `MutableConfigurationSource` and concrete Ozone configuration implementations. Depends on `TimeDurationUtil.ParsedTimeDuration`, `StorageUnit`, and Java `TimeUnit`.

## Risks
String formatting compatibility matters because generated values may later be parsed by `ConfigurationSource`. Unit suffix mapping must stay in sync with the parser.

## Test Signals
Tests should round-trip values through a mutable implementation for all primitive, time, storage, class, enum, and string-array setter paths.
