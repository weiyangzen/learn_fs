# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ReconfigurableConfig.java

## Purpose
Base class for annotated configuration POJOs that expose dynamic reconfiguration metadata and single-property updates.

## Important APIs, Types, And Functions
Public APIs are `reconfigurableProperties()` and `reconfigureProperty(String key, String value)`. It caches no explicit fields.

## Control Flow
`reconfigurableProperties` asks `ConfigurationReflectionUtil` for annotated fields marked reconfigurable. `reconfigureProperty` looks up the field by key and applies the new string value through reflection; unknown keys fail with `ConfigurationException`.

## State And Persistence
State is in subclass fields. Reconfiguration mutates those fields and invokes post-construct hooks as needed.

## Dependencies And Integration Points
Used by `ConfigurationExample` and production config classes that need runtime reconfiguration through `ReconfigurationHandler`.

## Risks
The property map is rebuilt on each call and only declared fields are considered. Misdeclared reconfigurable fields fail at runtime. Single-property updates depend on string parsing and field rollback semantics.

## Test Signals
Tests should verify listed keys, successful dynamic property changes, rejection of non-reconfigurable or unknown keys, and post-construct rollback behavior.
