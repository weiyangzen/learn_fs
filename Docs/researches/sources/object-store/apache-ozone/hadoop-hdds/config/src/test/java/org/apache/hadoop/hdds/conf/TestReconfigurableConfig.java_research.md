# sources/object-store/apache-ozone/hadoop-hdds/config/src/test/java/org/apache/hadoop/hdds/conf/TestReconfigurableConfig.java

## Purpose
Focused test for `ReconfigurableConfig.reconfigureProperty`.

## Important APIs, Types, And Functions
Uses `ConfigurationExample` created from `InMemoryConfigurationForTesting` and asserts the dynamic field changes after direct property reconfiguration.

## Control Flow
The test creates a default-injected object, calls `reconfigureProperty` with the dynamic key and new value, then reads the getter.

## State And Persistence
State is the mutable field inside `ConfigurationExample`; no external persistence.

## Dependencies And Integration Points
Covers the base class and reflection utility path for single-property reconfiguration.

## Risks
Only the successful path is covered. Unknown keys, non-reconfigurable keys, bad values, and post-construct rollback are not exercised.

## Test Signals
Signals include direct dynamic property update and preservation of the reflective conversion path.
