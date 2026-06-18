# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/StorageSize.java

## Purpose
Small value object representing a numeric storage size and its parsed `StorageUnit`.

## Important APIs, Types, And Functions
APIs include constructor, `parse(String)`, `parse(String, StorageUnit defaultUnit)`, `getUnit`, `getValue`, and `toString`. Parsing accepts long names, short names, and single-letter suffixes.

## Control Flow
Parsing trims and lowercases input, finds the first matching unit in `StorageUnit.values()` order, strips the longest matched suffix, parses the numeric part as double, and optionally falls back to a default unit when no suffix is found.

## State And Persistence
Instances are immutable with final unit and value fields. No persistence beyond string/XML configuration values.

## Dependencies And Integration Points
Used by `ConfigurationSource.getStorageSize` and `ConfigType.SIZE`; depends on `StorageUnit` conversion methods.

## Risks
Unit matching relies on enum order, especially bytes being last because suffix `b` overlaps other units. Values are doubles, so precision and later rounding/casting matter. Blank values throw `IllegalStateException`, while malformed values throw `IllegalArgumentException`.

## Test Signals
Tests should cover every suffix form, default-unit parsing, decimals, case/whitespace, invalid and blank strings, and overlap cases like `1mb` versus `1b`.
