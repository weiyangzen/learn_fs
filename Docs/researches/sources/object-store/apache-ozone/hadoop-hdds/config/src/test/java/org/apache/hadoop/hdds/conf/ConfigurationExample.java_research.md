# sources/object-store/apache-ozone/hadoop-hdds/config/src/test/java/org/apache/hadoop/hdds/conf/ConfigurationExample.java

## Purpose
Test fixture configuration POJO that exercises string, boolean, int, long time, `Duration`, size, double, reconfigurable, and prefix-containing config keys.

## Important APIs, Types, And Functions
Class is annotated `@ConfigGroup(prefix="ozone.test.config")` and extends `ReconfigurableConfig`. Fields use `@Config` with defaults, types, units, tags, and one `reconfigurable=true` property. Getters and selected setters expose test assertions.

## Control Flow
Tests create it through `ConfigurationSource.getObject`, causing reflection injection from defaults or in-memory overrides. Reconfiguration tests update only the dynamic field while non-reconfigurable fields remain unchanged.

## State And Persistence
State is private fields populated by injection. No external persistence except when written back through mutable configuration.

## Dependencies And Integration Points
Used by tests for reflection utility, configuration source, reconfiguration, and generated XML.

## Risks
As a test fixture, it must remain broad enough to cover supported types. Adding fields with invalid prefixes or defaults can break annotation-processor tests.

## Test Signals
Signals include injected default values, override values, generated XML entries, dynamic property listing, reconfiguration behavior, and set-from-object round trips.
