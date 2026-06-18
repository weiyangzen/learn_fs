# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigType.java

## Purpose
Enum implementing parsing and write-back behavior for supported configuration field types.

## Important APIs, Types, And Functions
Types include `AUTO`, `STRING`, `BOOLEAN`, `INT`, `LONG`, `TIME`, `SIZE`, `CLASS`, `DOUBLE`, and `FLOAT`. Each concrete type implements `parse()` and `set()` against `ConfigurationTarget`.

## Control Flow
Injection detects `AUTO` from field type, parses source strings into Java values, and assigns fields. Write-back converts Java values to configuration strings through target setters. Time supports `Duration` and long durations; size parses `StorageSize` and rounds bytes.

## State And Persistence
No persistent state. It is a stateless conversion table, but write-back mutates the supplied `ConfigurationTarget`.

## Dependencies And Integration Points
Depends on `TimeDurationUtil`, `StorageSize`, `StorageUnit`, `ConfigurationTarget`, and Java `Duration`/`TimeUnit`/`Class` loading.

## Risks
Type mismatch causes runtime `ConfigurationException`. `SIZE` narrows to `int` without range checking beyond Java cast. `CLASS` loads by class name and can fail late. `AUTO` intentionally throws if used directly.

## Test Signals
Tests should exercise every parse/set branch, `Duration` nanosecond versus millisecond write-back, size unit conversion, unsupported field types, class loading, and invalid numeric strings.
