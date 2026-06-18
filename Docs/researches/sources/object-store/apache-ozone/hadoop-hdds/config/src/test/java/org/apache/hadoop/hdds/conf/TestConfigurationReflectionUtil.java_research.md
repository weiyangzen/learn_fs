# sources/object-store/apache-ozone/hadoop-hdds/config/src/test/java/org/apache/hadoop/hdds/conf/TestConfigurationReflectionUtil.java

## Purpose
Tests metadata lookup and reconfigurable-property discovery in `ConfigurationReflectionUtil`.

## Important APIs, Types, And Functions
Parameterized data covers field names mapped to expected `ConfigType`, key, and default value. A separate test checks `mapReconfigurableProperties` returns only the dynamic config key.

## Control Flow
The test invokes `getType`, `getKey`, `getDefaultValue`, and `mapReconfigurableProperties` against `ConfigurationExample`, non-config classes, and missing fields.

## State And Persistence
No persistent state; all checks are in-memory reflection assertions.

## Dependencies And Integration Points
Covers reflection metadata APIs used by documentation, reconfiguration, and tests.

## Risks
Coverage does not directly test injection failure paths, post-construct behavior, or final field rejection.

## Test Signals
Signals include expected optionals for annotated fields, empty optionals for missing/non-annotated fields, and exact reconfigurable key set.
