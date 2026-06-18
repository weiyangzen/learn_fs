# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigurationReflectionUtil.java

## Purpose
Reflection engine for injecting configuration values into annotated POJOs, extracting metadata, updating targets from objects, and applying dynamic reconfiguration.

## Important APIs, Types, And Functions
Important APIs include `injectConfiguration`, `reconfigureProperty`, `mapReconfigurableProperties`, `updateConfiguration`, `getDefaultValue`, `getKey`, `getType`, and package-visible `callPostConstruct`. Helpers force private field access and reject final fields.

## Control Flow
Injection scans declared fields, skips non-reconfigurable fields during reconfiguration, reads source values with defaults, detects type when needed, parses through `ConfigType`, and force-sets fields. Single-property reconfiguration stores the old value, sets the new value, invokes `@PostConstruct`, and rolls back on post-construct failure.

## State And Persistence
State lives in target config objects. The utility mutates private fields and target configuration stores, but it persists nothing itself.

## Dependencies And Integration Points
Depends on `Config`, `ConfigType`, `ConfigurationSource`, `ConfigurationTarget`, `PostConstruct`, reflection APIs, and `Duration` detection.

## Risks
It scans only declared fields for injection and reconfigurable mapping, while metadata lookup walks superclasses. `Class.newInstance` callers require no-arg constructors. Access toggling can interact with newer Java access restrictions. Post-construct rollback covers the changed field but not other side effects.

## Test Signals
Tests should cover private fields, final-field rejection, reconfigurable filtering, post-construct invocation and rollback, superclass metadata lookup, null value write-back skipping, and all auto-detected types.
