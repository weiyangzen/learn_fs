# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigGroup.java

## Purpose
Runtime-retained type annotation that declares the common prefix for a configuration POJO.

## Important APIs, Types, And Functions
Single API member `prefix()` returns the expected prefix for `@Config.key()` values within the annotated class.

## Control Flow
The annotation processor finds classes with `@ConfigGroup`, then validates and writes enclosed `@Config` fields. Runtime code can use the annotation as descriptive metadata, though injection uses full keys from fields.

## State And Persistence
No mutable state; the prefix becomes part of compile-time validation and generated XML semantics.

## Dependencies And Integration Points
Integrated with `ConfigFileGenerator` and classes such as `ConfigurationExample` or production config POJOs.

## Risks
Prefix drift between class-level `ConfigGroup` and field-level full keys breaks generated config validation. The annotation does not enforce the prefix at runtime.

## Test Signals
Tests should include matching and non-matching prefixes and properties whose suffix itself contains the prefix-like text.
